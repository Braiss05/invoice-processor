"""Tests unitarios para parser.py."""

from datetime import date

from parser import parse_invoice_text

TEXTO_FACTURA_COMPLETA = """
ACME SOLUCIONES S.L.
CIF: B12345678
Factura nº: F-2026-0453
Fecha: 15/06/2026

Concepto: Servicios de consultoría
Base imponible: 1.000,00 EUR
IVA (21%): 210,00 EUR
Total: 1.210,00 EUR
"""

TEXTO_SIN_DATOS_RECONOCIBLES = """
Documento sin estructura clara de factura.
Algo de texto random sin CIF ni importes reconocibles.
"""


class TestParseInvoiceText:
    def test_extrae_empresa(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.company == "ACME SOLUCIONES S.L"

    def test_extrae_cif(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.tax_id == "B12345678"

    def test_extrae_fecha(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.invoice_date == date(2026, 6, 15)

    def test_extrae_numero_factura(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.invoice_number == "F-2026-0453"

    def test_extrae_base_imponible(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.taxable_base == 1000.0

    def test_extrae_iva(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.vat == 210.0

    def test_extrae_total(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.total == 1210.0

    def test_extrae_moneda(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.currency == "EUR"

    def test_factura_completa_marcada_como_completa(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "f.pdf")
        assert factura.is_complete() is True

    def test_source_file_se_conserva(self):
        factura = parse_invoice_text(TEXTO_FACTURA_COMPLETA, "mi_factura.pdf")
        assert factura.source_file == "mi_factura.pdf"

    def test_texto_sin_datos_no_lanza_excepcion(self):
        factura = parse_invoice_text(TEXTO_SIN_DATOS_RECONOCIBLES, "raro.pdf")
        assert factura is not None

    def test_texto_sin_datos_marca_incompleta(self):
        factura = parse_invoice_text(TEXTO_SIN_DATOS_RECONOCIBLES, "raro.pdf")
        assert factura.is_complete() is False

    def test_texto_sin_datos_campos_criticos_son_none(self):
        factura = parse_invoice_text(TEXTO_SIN_DATOS_RECONOCIBLES, "raro.pdf")
        assert factura.company is None
        assert factura.total is None