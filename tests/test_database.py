"""Tests unitarios para database.py.

Cada test usa una base de datos SQLite temporal y aislada (vía
monkeypatch de config.DATABASE_PATH), para no depender ni interferir
con la base de datos real del proyecto.
"""

from datetime import date

import pytest

import config
import database
from models import Invoice


@pytest.fixture
def db_temporal(tmp_path, monkeypatch):
    """Redirige config.DATABASE_PATH a un archivo temporal e inicializa la tabla."""
    ruta_temporal = tmp_path / "test_invoices.db"
    monkeypatch.setattr(config, "DATABASE_PATH", ruta_temporal)
    database.init_db()
    return ruta_temporal


def _crear_factura(**overrides) -> Invoice:
    """Helper para crear facturas de prueba con valores por defecto."""
    valores = dict(
        company="ACME SL",
        tax_id="B12345678",
        invoice_date=date(2026, 6, 15),
        invoice_number="F-001",
        taxable_base=1000.0,
        vat=210.0,
        total=1210.0,
        currency="EUR",
        source_file="f.pdf",
        text_hash="hash_unico_1",
    )
    valores.update(overrides)
    return Invoice(**valores)


class TestInsertInvoice:
    def test_inserta_y_asigna_id(self, db_temporal):
        factura = database.insert_invoice(_crear_factura())
        assert factura.id is not None

    def test_facturas_distintas_se_insertan_ambas(self, db_temporal):
        database.insert_invoice(_crear_factura(text_hash="hash_a"))
        database.insert_invoice(
            _crear_factura(tax_id="A87654321", invoice_number="F-002", text_hash="hash_b")
        )
        assert len(database.get_all_invoices()) == 2


class TestDuplicateDetection:
    def test_mismo_tax_id_y_numero_es_duplicado(self, db_temporal):
        database.insert_invoice(_crear_factura(text_hash="hash_a"))
        with pytest.raises(database.DuplicateInvoiceError):
            database.insert_invoice(_crear_factura(text_hash="hash_totalmente_distinto"))

    def test_mismo_text_hash_es_duplicado_aunque_falten_otros_campos(self, db_temporal):
        database.insert_invoice(
            _crear_factura(tax_id=None, invoice_number=None, text_hash="hash_compartido")
        )
        with pytest.raises(database.DuplicateInvoiceError):
            database.insert_invoice(
                _crear_factura(
                    tax_id=None,
                    invoice_number=None,
                    source_file="otro_archivo.pdf",
                    text_hash="hash_compartido",
                )
            )

    def test_excepcion_contiene_la_factura_existente(self, db_temporal):
        original = database.insert_invoice(_crear_factura(text_hash="hash_a"))
        with pytest.raises(database.DuplicateInvoiceError) as info:
            database.insert_invoice(_crear_factura(text_hash="hash_distinto"))
        assert info.value.existing_invoice.id == original.id


class TestSearchInvoices:
    def test_busqueda_por_empresa_parcial(self, db_temporal):
        database.insert_invoice(_crear_factura(company="ACME SOLUCIONES", text_hash="h1"))
        database.insert_invoice(
            _crear_factura(company="OTRA EMPRESA", tax_id="A1", invoice_number="F-2", text_hash="h2")
        )
        resultados = database.search_invoices("acme")
        assert len(resultados) == 1
        assert resultados[0].company == "ACME SOLUCIONES"

    def test_busqueda_sin_resultados_devuelve_lista_vacia(self, db_temporal):
        database.insert_invoice(_crear_factura(text_hash="h1"))
        assert database.search_invoices("empresa_inexistente") == []