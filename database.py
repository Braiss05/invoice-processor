"""Capa de persistencia: SQLite.

Gestiona la tabla de facturas, la detección de duplicados antes de
insertar, y las operaciones de listado/búsqueda. Es la única capa
del proyecto que sabe hablar SQL: si el día de mañana se migra a otro
motor de base de datos, solo este archivo cambia.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date
from typing import Iterator, List, Optional

import config
from models import Invoice
from utils import setup_logger

logger = setup_logger(__name__)


class DuplicateInvoiceError(Exception):
    """Se lanza al intentar insertar una factura ya existente en la base de datos."""

    def __init__(self, existing_invoice: Invoice):
        self.existing_invoice = existing_invoice
        super().__init__(
            f"Factura duplicada: ya existe con id={existing_invoice.id} "
            f"(source_file='{existing_invoice.source_file}')"
        )


_ESQUEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company         TEXT,
    tax_id          TEXT,
    invoice_date    TEXT,
    invoice_number  TEXT,
    taxable_base    REAL,
    vat             REAL,
    total           REAL,
    currency        TEXT NOT NULL,
    source_file     TEXT NOT NULL,
    text_hash       TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Proporciona una conexión SQLite con row_factory configurado.

    Se usa como context manager para garantizar que la conexión se
    cierra correctamente incluso si ocurre un error.
    """
    conexion = sqlite3.connect(config.DATABASE_PATH)
    conexion.row_factory = sqlite3.Row
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def init_db() -> None:
    """Crea la tabla de facturas si no existe. Debe llamarse al arrancar la app."""
    with get_connection() as conexion:
        conexion.execute(_ESQUEMA)
    logger.info("Base de datos inicializada en '%s'", config.DATABASE_PATH)


def _row_to_invoice(fila: sqlite3.Row) -> Invoice:
    """Convierte una fila de SQLite en un objeto Invoice."""
    fecha = date.fromisoformat(fila["invoice_date"]) if fila["invoice_date"] else None
    return Invoice(
        id=fila["id"],
        company=fila["company"],
        tax_id=fila["tax_id"],
        invoice_date=fecha,
        invoice_number=fila["invoice_number"],
        taxable_base=fila["taxable_base"],
        vat=fila["vat"],
        total=fila["total"],
        currency=fila["currency"],
        source_file=fila["source_file"],
        text_hash=fila["text_hash"],
    )


def find_duplicate(invoice: Invoice) -> Optional[Invoice]:
    """Busca si ya existe una factura equivalente en la base de datos.

    Estrategia de detección, en orden de prioridad:
    1. Si hay tax_id + invoice_number, se consideran duplicados exactos
       cuando ambos coinciden (una empresa no repite número de factura).
    2. Si no hay suficientes datos parseados, se recurre al hash del
       texto completo: mismo texto -> mismo PDF ya procesado.

    Args:
        invoice: La factura candidata a insertar.

    Returns:
        La factura ya existente si se encuentra un duplicado, o None.
    """
    with get_connection() as conexion:
        if invoice.tax_id and invoice.invoice_number:
            fila = conexion.execute(
                "SELECT * FROM invoices WHERE tax_id = ? AND invoice_number = ?",
                (invoice.tax_id, invoice.invoice_number),
            ).fetchone()
            if fila:
                return _row_to_invoice(fila)

        fila = conexion.execute(
            "SELECT * FROM invoices WHERE text_hash = ?", (invoice.text_hash,)
        ).fetchone()
        if fila:
            return _row_to_invoice(fila)

    return None


def insert_invoice(invoice: Invoice) -> Invoice:
    """Inserta una factura en la base de datos si no es un duplicado.

    Args:
        invoice: La factura a persistir (su campo id debe ser None).

    Returns:
        La misma factura con el id asignado por SQLite.

    Raises:
        DuplicateInvoiceError: si ya existe una factura equivalente.
    """
    duplicado = find_duplicate(invoice)
    if duplicado is not None:
        logger.warning(
            "Factura duplicada detectada para '%s' (ya existe id=%d)",
            invoice.source_file,
            duplicado.id,
        )
        raise DuplicateInvoiceError(duplicado)

    with get_connection() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO invoices (
                company, tax_id, invoice_date, invoice_number,
                taxable_base, vat, total, currency, source_file, text_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invoice.company,
                invoice.tax_id,
                invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                invoice.invoice_number,
                invoice.taxable_base,
                invoice.vat,
                invoice.total,
                invoice.currency,
                invoice.source_file,
                invoice.text_hash,
            ),
        )
        invoice.id = cursor.lastrowid

    logger.info("Factura insertada: id=%d, source_file='%s'", invoice.id, invoice.source_file)
    return invoice


def get_all_invoices() -> List[Invoice]:
    """Devuelve todas las facturas almacenadas, ordenadas por fecha de creación descendente."""
    with get_connection() as conexion:
        filas = conexion.execute(
            "SELECT * FROM invoices ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_invoice(fila) for fila in filas]


def search_invoices(query: str) -> List[Invoice]:
    """Busca facturas por empresa, CIF/NIF o número de factura.

    La búsqueda es parcial (LIKE) e insensible a mayúsculas/minúsculas.

    Args:
        query: Texto a buscar.

    Returns:
        Lista de facturas que coinciden con la búsqueda.
    """
    patron = f"%{query.strip()}%"
    with get_connection() as conexion:
        filas = conexion.execute(
            """
            SELECT * FROM invoices
            WHERE company LIKE ? COLLATE NOCASE
               OR tax_id LIKE ? COLLATE NOCASE
               OR invoice_number LIKE ? COLLATE NOCASE
            ORDER BY created_at DESC
            """,
            (patron, patron, patron),
        ).fetchall()
    return [_row_to_invoice(fila) for fila in filas]