"""Tests unitarios para utils.py."""

from datetime import date

from utils import (
    compute_text_hash,
    normalize_whitespace,
    parse_spanish_amount,
    parse_spanish_date,
)


class TestParseSpanishAmount:
    def test_importe_con_miles_y_decimales(self):
        assert parse_spanish_amount("1.234,56") == 1234.56

    def test_importe_simple_con_decimales(self):
        assert parse_spanish_amount("121,00") == 121.0

    def test_importe_sin_decimales(self):
        assert parse_spanish_amount("50") == 50.0

    def test_importe_con_simbolo_euro(self):
        assert parse_spanish_amount("121,00 €") == 121.0

    def test_texto_invalido_devuelve_none(self):
        assert parse_spanish_amount("no es un numero") is None

    def test_cadena_vacia_devuelve_none(self):
        assert parse_spanish_amount("") is None


class TestParseSpanishDate:
    def test_formato_barra(self):
        assert parse_spanish_date("15/06/2026") == date(2026, 6, 15)

    def test_formato_guion(self):
        assert parse_spanish_date("15-06-2026") == date(2026, 6, 15)

    def test_formato_punto(self):
        assert parse_spanish_date("15.06.2026") == date(2026, 6, 15)

    def test_fecha_invalida_devuelve_none(self):
        assert parse_spanish_date("no es una fecha") is None

    def test_cadena_vacia_devuelve_none(self):
        assert parse_spanish_date("") is None


class TestNormalizeWhitespace:
    def test_colapsa_espacios_multiples(self):
        assert normalize_whitespace("Hola    Mundo") == "Hola Mundo"

    def test_colapsa_saltos_de_linea(self):
        assert normalize_whitespace("Hola\n\n\nMundo") == "Hola Mundo"

    def test_elimina_espacios_en_extremos(self):
        assert normalize_whitespace("   Hola Mundo   ") == "Hola Mundo"


class TestComputeTextHash:
    def test_mismo_texto_produce_mismo_hash(self):
        h1 = compute_text_hash("Factura 123")
        h2 = compute_text_hash("Factura 123")
        assert h1 == h2

    def test_texto_con_espaciado_distinto_produce_mismo_hash(self):
        h1 = compute_text_hash("Factura   123")
        h2 = compute_text_hash("Factura 123")
        assert h1 == h2

    def test_textos_distintos_producen_hashes_distintos(self):
        h1 = compute_text_hash("Factura 123")
        h2 = compute_text_hash("Factura 456")
        assert h1 != h2