"""Detección de PDFs escaneados y extracción de texto vía OCR.

Este módulo aísla toda la lógica de "visión por computador": renderizar
páginas de PDF como imágenes, mejorarlas con OpenCV, y extraer el texto
con Tesseract. extractor.py solo delega aquí cuando detecta que un PDF
no tiene capa de texto nativa.
"""

import numpy as np
import cv2
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image

import config
from utils import normalize_whitespace, setup_logger

logger = setup_logger(__name__)

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def is_scanned_pdf(pdf_path: str) -> bool:
    """Determina si un PDF es una imagen escaneada o tiene texto nativo.

    Heurística: intenta extraer texto con pdfplumber. Si el total de
    caracteres útiles está por debajo del umbral configurado, se asume
    que el PDF no tiene capa de texto (es una imagen escaneada).

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        True si se considera que el PDF es escaneado (necesita OCR).
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_text = "".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        logger.exception("Error al abrir '%s' con pdfplumber", pdf_path)
        # Si ni siquiera se puede abrir con pdfplumber, probamos con OCR
        # como último recurso.
        return True

    caracteres_utiles = len(normalize_whitespace(total_text))
    es_escaneado = caracteres_utiles < config.MIN_TEXT_CHARS_THRESHOLD

    logger.debug(
        "'%s' tiene %d caracteres útiles (umbral=%d) -> escaneado=%s",
        pdf_path,
        caracteres_utiles,
        config.MIN_TEXT_CHARS_THRESHOLD,
        es_escaneado,
    )
    return es_escaneado


def render_page_as_image(pdf_path: str, page_number: int, dpi: int = 300) -> Image.Image:
    """Renderiza una página de un PDF como imagen PIL.

    Un DPI más alto mejora la precisión del OCR pero es más lento.
    300 DPI es el estándar recomendado por Tesseract.

    Args:
        pdf_path: Ruta al archivo PDF.
        page_number: Índice de página (empezando en 0).
        dpi: Resolución de renderizado.

    Returns:
        La página renderizada como imagen PIL en modo RGB.
    """
    with fitz.open(pdf_path) as documento:
        pagina = documento[page_number]
        zoom = dpi / 72  # 72 DPI es la resolución base de PDF
        matriz = fitz.Matrix(zoom, zoom)
        pixmap = pagina.get_pixmap(matrix=matriz)
        return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def preprocess_image_for_ocr(image: Image.Image) -> np.ndarray:
    """Aplica preprocesado con OpenCV para mejorar la precisión del OCR.

    Pasos: escala de grises -> desenfoque para reducir ruido ->
    umbralizado adaptativo (binarización), que suele mejorar
    notablemente el reconocimiento en escaneos de baja calidad.

    Args:
        image: Imagen PIL de la página.

    Returns:
        Imagen procesada como array de NumPy, lista para Tesseract.
    """
    array = np.array(image)
    gris = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    desenfocada = cv2.GaussianBlur(gris, (5, 5), 0)
    binaria = cv2.adaptiveThreshold(
        desenfocada,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=11,
    )
    return binaria


def extract_text_with_ocr(pdf_path: str) -> str:
    """Extrae el texto completo de un PDF escaneado usando OCR.

    Recorre todas las páginas, las renderiza, las preprocesa con OpenCV
    y aplica Tesseract a cada una, concatenando el resultado.

    Args:
        pdf_path: Ruta al archivo PDF.

    Returns:
        El texto reconocido de todas las páginas, concatenado.
    """
    with fitz.open(pdf_path) as documento:
        num_paginas = documento.page_count

    fragmentos_texto = []
    for numero_pagina in range(num_paginas):
        try:
            imagen = render_page_as_image(pdf_path, numero_pagina)
            imagen_procesada = preprocess_image_for_ocr(imagen)
            texto_pagina = pytesseract.image_to_string(
                imagen_procesada, lang=config.OCR_LANGUAGE
            )
            fragmentos_texto.append(texto_pagina)
        except Exception:
            logger.exception(
                "Error de OCR en '%s', página %d", pdf_path, numero_pagina
            )

    texto_completo = "\n".join(fragmentos_texto)
    logger.info(
        "OCR completado para '%s': %d páginas, %d caracteres extraídos",
        pdf_path,
        num_paginas,
        len(texto_completo),
    )
    return texto_completo