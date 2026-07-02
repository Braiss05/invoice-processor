"""Funciones de utilidad reutilizadas por el resto de módulos.

Incluye configuración de logging y funciones puras de normalización
de texto, fechas e importes. Ningún módulo debe usar print() para
depurar: todos usan el logger configurado aquí.
"""

import hashlib
import logging
import re
from datetime import date, datetime
from typing import Optional

import config


def setup_logger(name: str) -> logging.Logger:
    """Crea (o reutiliza) un logger configurado para escribir en archivo y consola.

    Args:
        name: Nombre del logger, normalmente __name__ del módulo que lo llama.

    Returns:
        Una instancia de logging.Logger lista para usar.
    """
    logger = logging.getLogger(name)

    # Evita añadir handlers duplicados si el logger ya fue configurado
    # (puede pasar si el módulo se importa varias veces en Streamlit).
    if logger.handlers:
        return logger

    logger.setLevel(config.LOG_LEVEL)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def normalize_whitespace(text: str) -> str:
    """Colapsa espacios, tabulaciones y saltos de línea múltiples en uno solo.

    Necesario porque el texto extraído de PDFs (sobre todo vía OCR) suele
    venir con espaciado irregular que rompe las expresiones regulares.
    """
    return re.sub(r"\s+", " ", text).strip()


def parse_spanish_amount(raw: str) -> Optional[float]:
    """Convierte un importe en formato español ("1.234,56") a float.

    Formato español: punto como separador de miles, coma como decimal.
    Ejemplos: "1.234,56" -> 1234.56 | "121,00" -> 121.0 | "50" -> 50.0

    Args:
        raw: El importe en texto, tal como aparece en la factura.

    Returns:
        El importe como float, o None si no se pudo parsear.
    """
    if not raw:
        return None

    cleaned = raw.strip().replace("€", "").replace(" ", "")
    cleaned = cleaned.replace(".", "").replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_spanish_date(raw: str) -> Optional[date]:
    """Parsea una fecha en formatos habituales de facturas españolas.

    Soporta: "dd/mm/yyyy", "dd-mm-yyyy", "dd.mm.yyyy".

    Args:
        raw: La fecha en texto tal como aparece en la factura.

    Returns:
        Un objeto date, o None si ningún formato coincide.
    """
    if not raw:
        return None

    raw = raw.strip()
    formatos = ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y")

    for formato in formatos:
        try:
            return datetime.strptime(raw, formato).date()
        except ValueError:
            continue

    return None


def compute_text_hash(text: str) -> str:
    """Calcula un hash SHA-256 del texto extraído de un PDF.

    Se usa como identificador de respaldo para detectar facturas
    duplicadas cuando no se pudo extraer un número de factura fiable.
    """
    normalized = normalize_whitespace(text).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()