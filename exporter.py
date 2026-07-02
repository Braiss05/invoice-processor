"""Exportación de facturas a Excel.

Convierte una lista de objetos Invoice en un archivo .xlsx usando
Pandas. No accede a la base de datos directamente: recibe los datos
ya obtenidos, para poder testearse sin SQLite real.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

import config
from models import Invoice
from utils import setup_logger

logger = setup_logger(__name__)

# Encabezados en español, en el orden en que deben aparecer en el Excel.
_COLUMNAS = {
    "id": "ID",
    "company": "Empresa",
    "tax_id": "CIF/NIF",
    "invoice_date": "Fecha",
    "invoice_number": "Nº Factura",
    "taxable_base": "Base Imponible",
    "vat": "IVA",
    "total": "Total",
    "currency": "Moneda",
    "source_file": "Archivo Origen",
}


def _build_dataframe(invoices: List[Invoice]) -> pd.DataFrame:
    """Construye un DataFrame de Pandas a partir de una lista de facturas."""
    filas = [invoice.to_dict() for invoice in invoices]
    df = pd.DataFrame(filas, columns=_COLUMNAS.keys())
    return df.rename(columns=_COLUMNAS)


def export_to_excel(invoices: List[Invoice], filename: Optional[str] = None) -> Path:
    """Exporta una lista de facturas a un archivo Excel en exports/.

    Args:
        invoices: Las facturas a exportar (normalmente, el resultado de
            database.get_all_invoices() o database.search_invoices()).
        filename: Nombre del archivo de salida. Si no se indica, se genera
            uno con marca de tiempo (ej. "facturas_20260702_1230.xlsx").

    Returns:
        La ruta al archivo Excel generado.
    """
    if filename is None:
        marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"facturas_{marca_tiempo}.xlsx"

    ruta_salida = config.EXPORTS_DIR / filename

    df = _build_dataframe(invoices)
    df.to_excel(ruta_salida, index=False, sheet_name="Facturas", engine="openpyxl")

    logger.info(
        "Exportadas %d facturas a '%s'", len(invoices), ruta_salida
    )
    return ruta_salida