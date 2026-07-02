"""Modelos de datos del dominio.

Define la estructura Invoice, el contrato de datos que usan
parser.py, database.py y exporter.py.
"""

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional


@dataclass
class Invoice:
    """Representa una factura extraída de un PDF.

    Attributes:
        company: Nombre de la empresa emisora.
        tax_id: CIF/NIF del emisor.
        invoice_date: Fecha de la factura.
        invoice_number: Número/identificador de la factura.
        taxable_base: Base imponible (importe antes de impuestos).
        vat: Importe de IVA aplicado.
        total: Importe total de la factura.
        currency: Código de moneda (ej. "EUR").
        source_file: Nombre del PDF de origen.
        text_hash: Hash del texto extraído. Se usa como respaldo para
            detectar duplicados cuando el número de factura no se
            pudo parsear correctamente.
        id: Identificador autoincremental en la base de datos.
            Es None hasta que la factura se persiste.
    """

    company: Optional[str]
    tax_id: Optional[str]
    invoice_date: Optional[date]
    invoice_number: Optional[str]
    taxable_base: Optional[float]
    vat: Optional[float]
    total: Optional[float]
    currency: str
    source_file: str
    text_hash: str
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convierte la factura a un diccionario serializable (ej. para JSON o Streamlit)."""
        data = asdict(self)
        if self.invoice_date is not None:
            data["invoice_date"] = self.invoice_date.isoformat()
        return data

    def is_complete(self) -> bool:
        """Indica si se extrajeron todos los campos críticos del negocio.

        Se usa para marcar visualmente en la interfaz las facturas que
        necesitan revisión manual porque el parser no pudo extraer
        algún campo obligatorio.
        """
        campos_criticos = (
            self.company,
            self.tax_id,
            self.invoice_date,
            self.invoice_number,
            self.total,
        )
        return all(campo is not None for campo in campos_criticos)