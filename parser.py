"""Parseo de texto de factura a campos estructurados.

Convierte el texto plano extraído por extractor.py en un objeto Invoice,
usando expresiones regulares y heurísticas específicas del formato
habitual de facturas españolas. Es el único módulo que "sabe" cómo
se ven los campos dentro del texto.
"""

import re
from typing import Optional

import config
from models import Invoice
from utils import compute_text_hash, parse_spanish_amount, parse_spanish_date, setup_logger

logger = setup_logger(__name__)

# --- Patrones de expresiones regulares (compilados una sola vez) ---

# CIF: letra + 7 dígitos + letra/dígito de control. NIF: 8 dígitos + letra.
PATRON_CIF_NIF = re.compile(
    r"\b([A-HJNP-SUVW]\d{7}[0-9A-J]|\d{8}[A-Z])\b", re.IGNORECASE
)

PATRON_FECHA = re.compile(r"\b(\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4})\b")

PATRON_NUMERO_FACTURA = re.compile(
    r"(?:factura|invoice)\s*(?:n[ºo°]?\.?|number|num\.?)?\s*:?\s*"
    r"([A-Z0-9][A-Z0-9\-/]{2,20})",
    re.IGNORECASE,
)

PATRON_BASE_IMPONIBLE = re.compile(
    r"base\s+imponible\s*:?\s*([\d.,]+)\s*(?:€|eur)?", re.IGNORECASE
)

PATRON_IVA = re.compile(
    r"iva\s*(?:\(\s*\d{1,2}\s*%\s*\))?\s*:?\s*([\d.,]+)\s*(?:€|eur)?",
    re.IGNORECASE,
)

PATRON_TOTAL = re.compile(
    r"total\s*(?:factura)?\s*:?\s*([\d.,]+)\s*(?:€|eur)?", re.IGNORECASE
)

# Formas jurídicas habituales para localizar el nombre de la empresa.
FORMAS_JURIDICAS = r"(?:S\.?L\.?U?\.?|S\.?A\.?U?\.?|S\.?COOP\.?|S\.?C\.?)"
PATRON_EMPRESA = re.compile(
    rf"([A-ZÁÉÍÓÚÑ][\w.,&\-\s]{{2,60}}?\s+{FORMAS_JURIDICAS})\b",
    re.IGNORECASE,
)

PATRON_MONEDA = re.compile(r"\b(EUR|USD|GBP|€|\$|£)\b")

_SIMBOLO_A_CODIGO = {"€": "EUR", "$": "USD", "£": "GBP"}


def _extract_tax_id(text: str) -> Optional[str]:
    """Busca un CIF o NIF español en el texto."""
    coincidencia = PATRON_CIF_NIF.search(text)
    return coincidencia.group(1).upper() if coincidencia else None


def _extract_date(text: str) -> Optional[str]:
    """Busca la primera fecha con formato dd/mm/yyyy (u similar) en el texto."""
    coincidencia = PATRON_FECHA.search(text)
    return coincidencia.group(1) if coincidencia else None


def _extract_invoice_number(text: str) -> Optional[str]:
    """Busca el número de factura tras palabras clave como 'Factura nº'."""
    coincidencia = PATRON_NUMERO_FACTURA.search(text)
    return coincidencia.group(1).strip() if coincidencia else None


def _extract_amount(pattern: re.Pattern, text: str) -> Optional[str]:
    """Aplica un patrón de importe y devuelve el texto crudo capturado."""
    coincidencia = pattern.search(text)
    return coincidencia.group(1) if coincidencia else None


def _extract_company(text: str) -> Optional[str]:
    """Busca el nombre de la empresa a partir de su forma jurídica (S.L., S.A....)."""
    coincidencia = PATRON_EMPRESA.search(text)
    if not coincidencia:
        return None
    return re.sub(r"\s+", " ", coincidencia.group(1)).strip()


def _extract_currency(text: str) -> str:
    """Detecta la moneda usada en la factura; si no se encuentra, usa la de config."""
    coincidencia = PATRON_MONEDA.search(text)
    if not coincidencia:
        return config.DEFAULT_CURRENCY
    valor = coincidencia.group(1)
    return _SIMBOLO_A_CODIGO.get(valor, valor.upper())


def parse_invoice_text(text: str, source_file: str) -> Invoice:
    """Convierte el texto extraído de una factura en un objeto Invoice.

    Ningún campo es obligatorio a nivel de parseo: si algo no se
    encuentra, queda como None y la factura se marca como incompleta
    (ver Invoice.is_complete()) para que app.py pueda señalarla para
    revisión manual.

    Args:
        text: Texto plano ya extraído (normalizado) del PDF.
        source_file: Nombre del archivo PDF de origen, para trazabilidad.

    Returns:
        Un objeto Invoice con los campos detectados.
    """
    fecha_cruda = _extract_date(text)
    base_cruda = _extract_amount(PATRON_BASE_IMPONIBLE, text)
    iva_crudo = _extract_amount(PATRON_IVA, text)
    total_crudo = _extract_amount(PATRON_TOTAL, text)

    factura = Invoice(
        company=_extract_company(text),
        tax_id=_extract_tax_id(text),
        invoice_date=parse_spanish_date(fecha_cruda) if fecha_cruda else None,
        invoice_number=_extract_invoice_number(text),
        taxable_base=parse_spanish_amount(base_cruda) if base_cruda else None,
        vat=parse_spanish_amount(iva_crudo) if iva_crudo else None,
        total=parse_spanish_amount(total_crudo) if total_crudo else None,
        currency=_extract_currency(text),
        source_file=source_file,
        text_hash=compute_text_hash(text),
    )

    if not factura.is_complete():
        logger.warning(
            "Factura incompleta tras el parseo: '%s' (company=%s, tax_id=%s, "
            "date=%s, number=%s, total=%s)",
            source_file,
            factura.company,
            factura.tax_id,
            factura.invoice_date,
            factura.invoice_number,
            factura.total,
        )
    else:
        logger.info("Factura parseada correctamente: '%s'", source_file)

    return factura