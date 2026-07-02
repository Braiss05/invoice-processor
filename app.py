"""Interfaz Streamlit de Invoice Processor.

Capa de presentación: sube PDFs, dispara el pipeline de extracción/
parseo/persistencia, y permite buscar y exportar facturas. No contiene
lógica de negocio propia; toda vive en extractor.py, parser.py,
database.py y exporter.py.
"""

from pathlib import Path
from typing import List, Tuple

import pandas as pd
import streamlit as st

import config
from database import DuplicateInvoiceError, get_all_invoices, init_db, insert_invoice, search_invoices
from exporter import export_to_excel
from extractor import PDFExtractionError, extract_text_from_pdf
from models import Invoice
from parser import parse_invoice_text
from utils import setup_logger

logger = setup_logger(__name__)


def guardar_pdf_subido(archivo_subido) -> Path:
    """Guarda un archivo subido por Streamlit en la carpeta invoices/.

    Args:
        archivo_subido: Objeto UploadedFile de Streamlit.

    Returns:
        La ruta local donde se guardó el PDF.
    """
    ruta_destino = config.INVOICES_DIR / archivo_subido.name
    ruta_destino.write_bytes(archivo_subido.getbuffer())
    return ruta_destino


def procesar_pdf(ruta_pdf: Path, nombre_original: str) -> Tuple[str, str]:
    """Ejecuta el pipeline completo sobre un PDF: extraer, parsear, guardar.

    Args:
        ruta_pdf: Ruta local del PDF ya guardado.
        nombre_original: Nombre del archivo, para trazabilidad y mensajes.

    Returns:
        Una tupla (estado, detalle) legible para mostrar en la interfaz.
    """
    try:
        texto = extract_text_from_pdf(str(ruta_pdf))
        factura = parse_invoice_text(texto, nombre_original)
        factura_guardada = insert_invoice(factura)
    except DuplicateInvoiceError as error:
        return "⚠️ Duplicada", f"Ya existe (id={error.existing_invoice.id})"
    except PDFExtractionError as error:
        logger.error("Error de extracción en '%s': %s", nombre_original, error)
        return "❌ Error de extracción", str(error)
    except Exception as error:  # noqa: BLE001 - queremos capturar cualquier fallo inesperado
        logger.exception("Error inesperado procesando '%s'", nombre_original)
        return "❌ Error inesperado", str(error)

    if factura_guardada.is_complete():
        return "✅ Procesada", f"id={factura_guardada.id}"
    return "⚠️ Procesada (incompleta)", f"id={factura_guardada.id} — revisar campos vacíos"


def render_subida_de_facturas() -> None:
    """Sección de la barra lateral para subir y procesar PDFs."""
    st.sidebar.header("📤 Subir facturas")
    archivos = st.sidebar.file_uploader(
        "Selecciona uno o varios PDF", type=["pdf"], accept_multiple_files=True
    )
    procesar = st.sidebar.button("Procesar facturas", disabled=not archivos)

    if not (procesar and archivos):
        return

    barra_progreso = st.sidebar.progress(0)
    resultados: List[Tuple[str, str, str]] = []

    for indice, archivo in enumerate(archivos):
        ruta_local = guardar_pdf_subido(archivo)
        estado, detalle = procesar_pdf(ruta_local, archivo.name)
        resultados.append((archivo.name, estado, detalle))
        barra_progreso.progress((indice + 1) / len(archivos))

    st.subheader("Resultado del procesamiento")
    st.table(pd.DataFrame(resultados, columns=["Archivo", "Estado", "Detalle"]))


def render_tabla_facturas(facturas: List[Invoice]) -> None:
    """Muestra la tabla de facturas, marcando visualmente las incompletas."""
    if not facturas:
        st.info("No hay facturas que coincidan con la búsqueda.")
        return

    filas = []
    for factura in facturas:
        fila = factura.to_dict()
        fila["completa"] = "✅" if factura.is_complete() else "⚠️"
        filas.append(fila)

    df = pd.DataFrame(filas)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_seccion_exportar(facturas: List[Invoice]) -> None:
    """Botón de exportación a Excel de las facturas actualmente mostradas."""
    if st.button("📥 Exportar a Excel", disabled=not facturas):
        ruta_excel = export_to_excel(facturas)
        with open(ruta_excel, "rb") as archivo_excel:
            st.download_button(
                "Descargar Excel generado",
                data=archivo_excel,
                file_name=ruta_excel.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        st.success(f"Excel generado: {ruta_excel.name}")


def main() -> None:
    """Punto de entrada de la aplicación Streamlit."""
    st.set_page_config(page_title="Invoice Processor", page_icon="🧾", layout="wide")
    init_db()

    st.title("🧾 Invoice Processor")
    st.caption("Extracción automática de facturas PDF (texto nativo u OCR) con almacenamiento en SQLite.")

    render_subida_de_facturas()

    st.divider()
    st.subheader("Facturas almacenadas")

    columna_busqueda, columna_exportar = st.columns([3, 1])
    with columna_busqueda:
        consulta = st.text_input("Buscar por empresa, CIF/NIF o número de factura")

    facturas = search_invoices(consulta) if consulta else get_all_invoices()

    render_tabla_facturas(facturas)

    with columna_exportar:
        st.write("")
        render_seccion_exportar(facturas)


if __name__ == "__main__":
    main()