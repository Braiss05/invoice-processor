# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue Keep a Changelog, y este proyecto sigue Versionado Semántico.

## [1.0.0] - 2026-07-02

### Añadido

- config.py: carga centralizada de configuración vía .env.
- models.py: dataclass Invoice como contrato de datos del dominio.
- utils.py: logging configurado, normalización de texto, parseo de fechas e importes en formato español, hash de texto para duplicados.
- ocr.py: detección de PDFs escaneados, renderizado de páginas (PyMuPDF), preprocesado de imagen (OpenCV) y extracción de texto (Tesseract OCR).
- extractor.py: orquestador de extracción de texto, con decisión automática entre lectura nativa (pdfplumber) y OCR.
- parser.py: extracción de campos estructurados (empresa, CIF/NIF, fecha, número de factura, base imponible, IVA, total, moneda) mediante expresiones regulares.
- database.py: persistencia en SQLite, detección de facturas duplicadas (por CIF+número de factura, o por hash de texto) y búsqueda.
- exporter.py: exportación de facturas a Excel vía Pandas.
- app.py: interfaz Streamlit completa (subida de PDFs, procesamiento, tabla de resultados, búsqueda y exportación a Excel).
- Suite de 37 tests unitarios (tests/test_utils.py, tests/test_parser.py, tests/test_database.py).
- Documentación profesional: README.md, LICENSE (MIT), CONTRIBUTING.md.

### Corregido

- Extracción del número de factura: el patrón de expresión regular capturaba erróneamente la propia palabra "Factura" del título del documento en vez del código real. Se añadió una validación de que el candidato contenga al menos un dígito.
- Orden de lectura del OCR en documentos con estructura de tabla (como las facturas): se fijó el modo de segmentación de Tesseract a --psm 6 (bloque uniforme de texto), que evita que se mezclen las columnas de conceptos e importes.

## [Unreleased]

### Por hacer (ver "Futuras mejoras" en el README)

- Extracción de líneas de detalle (conceptos individuales).
- Panel de estadísticas de gasto.
- Edición manual de campos incompletos desde la interfaz.
- Exportación adicional a CSV/JSON.
- Soporte multi-idioma en el parser.
- Dockerfile para despliegue sin instalación manual de Tesseract.