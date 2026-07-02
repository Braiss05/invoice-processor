"""Orquestador de extracción de texto de PDFs.

Decide, para cada PDF, si tiene texto nativo (lo extrae con pdfplumber)
o si es un escaneado (delega en ocr.py). Es el único punto de entrada
del pipeline documental: parser.py nunca abre un PDF directamente.
"""

import pdfplumber

from ocr import extract_text_with_ocr, is_scanned_pdf
from utils import normalize_whitespace, setup_logger

logger = setup_logger(__name__)


class PDFExtractionError(Exception):
    """Se lanza cuando un PDF no puede procesarse en absoluto."""


def extract_native_text(pdf_path: str) -> str:
    """Extrae el texto de un PDF que tiene capa de texto nativa.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        El texto de todas las páginas, concatenado.
    """
    with pdfplumber.open(pdf_path) as pdf:
        paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
    return "\n".join(paginas)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae el texto completo de un PDF, usando OCR solo si es necesario.

    Este es el punto de entrada que debe usar el resto de la aplicación
    (parser.py, app.py). Internamente decide la estrategia de extracción.

    Args:
        pdf_path: Ruta al archivo PDF a procesar.

    Returns:
        El texto extraído, normalizado (espacios colapsados).

    Raises:
        PDFExtractionError: si el PDF no se puede leer por ninguna vía.
    """
    try:
        if is_scanned_pdf(pdf_path):
            logger.info("'%s' detectado como escaneado -> usando OCR", pdf_path)
            texto_crudo = extract_text_with_ocr(pdf_path)
        else:
            logger.info("'%s' detectado con texto nativo -> usando pdfplumber", pdf_path)
            texto_crudo = extract_native_text(pdf_path)
    except Exception as error:
        logger.exception("Fallo irrecuperable extrayendo texto de '%s'", pdf_path)
        raise PDFExtractionError(
            f"No se pudo extraer texto de '{pdf_path}': {error}"
        ) from error

    texto_normalizado = normalize_whitespace(texto_crudo)

    if not texto_normalizado:
        logger.warning("'%s' no produjo ningún texto extraíble", pdf_path)

    return texto_normalizado