<img width="1917" height="1025" alt="Captura de pantalla 2026-07-08 111100" src="https://github.com/user-attachments/assets/9018100e-98d4-432a-adce-dc7036ff0082" />
<img width="990" height="683" alt="Captura de pantalla 2026-07-08 111355" src="https://github.com/user-attachments/assets/64a301ee-9349-439d-8456-14f8e366fec1" />
<img width="1917" height="1028" alt="Captura de pantalla 2026-07-08 111120" src="https://github.com/user-attachments/assets/6acab565-a958-40cb-99ef-32c4bd3160d7" />
<img width="1920" height="1080" alt="Captura de pantalla 2026-07-08 111526" src="https://github.com/user-attachments/assets/4b2f527d-deb7-4480-8a1a-de0bcbd6bd7c" />


Descripción

Invoice Processor automatiza la lectura de facturas en PDF: detecta si el documento tiene texto nativo o es una imagen escaneada, aplica OCR cuando es necesario, extrae los campos clave (empresa, CIF/NIF, fecha, número de factura, base imponible, IVA, total y moneda), los guarda en una base de datos SQLite evitando duplicados, y permite buscarlos y exportarlos a Excel desde una interfaz web sencilla.

Pensado como proyecto de portfolio siguiendo buenas prácticas de ingeniería de software: separación de responsabilidades, type hints, docstrings, logging, tests unitarios y configuración externalizada.

Arquitectura

El proyecto sigue un pipeline lineal con separación estricta de responsabilidades: cada módulo tiene una única razón para cambiar.


<img width="752" height="710" alt="image" src="https://github.com/user-attachments/assets/e1699f83-4ba2-401e-9a3b-057243e38ed9" />


## Responsabilidad de cada módulo

| Módulo | Responsabilidad |
|--------|-----------------|
| **config.py** | Carga el archivo `.env` y expone rutas y constantes tipadas. Ningún otro módulo lee variables de entorno directamente. |
| **models.py** | Define la dataclass `Invoice`, utilizada como contrato de datos único entre `parser`, `database` y `exporter`. |
| **utils.py** | Configura el sistema de logging, normaliza texto, convierte fechas e importes en formato español y genera hashes de texto. |
| **ocr.py** | Detecta si un PDF es escaneado; renderiza las páginas con **PyMuPDF**, las preprocesa con **OpenCV** y aplica OCR mediante **Tesseract**. |
| **extractor.py** | Orquesta la extracción de texto. Decide entre usar **pdfplumber** (texto nativo) o `ocr.py` (PDF escaneado). |
| **parser.py** | Convierte el texto plano en datos estructurados mediante expresiones regulares. |
| **database.py** | Gestiona la persistencia en **SQLite**, la detección de duplicados y las operaciones de búsqueda. |
| **exporter.py** | Exporta listas de facturas a archivos **Excel (`.xlsx`)** utilizando **Pandas**. |
| **app.py** | Implementa la interfaz de usuario con **Streamlit**. Contiene únicamente la capa de presentación, sin lógica de negocio. |


 ## Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
|------------|--------------------|
| **Python 3.11+** | Lenguaje base del proyecto. |
| **Streamlit** | Interfaz web interactiva sin necesidad de un frontend separado. |
| **pdfplumber** | Extracción de texto de PDFs con capa de texto nativa. |
| **PyMuPDF (fitz)** | Renderizado rápido de páginas PDF como imágenes para el proceso de OCR. |
| **pytesseract + Tesseract OCR** | Reconocimiento óptico de caracteres sobre facturas escaneadas. |
| **OpenCV** | Preprocesado de imágenes (escala de grises, desenfoque y umbralizado adaptativo) para mejorar la precisión del OCR. |
| **SQLite** | Base de datos embebida, sin necesidad de un servidor externo. |
| **Pandas + openpyxl** | Exportación de datos a archivos Excel (`.xlsx`). |
| **python-dotenv** | Gestión de la configuración mediante variables de entorno (`.env`). |
| **pytest** | Ejecución de tests unitarios (37 pruebas sobre `utils`, `parser` y `database`). |


## Estructura del proyecto

```text
invoice-processor/
│
├── app.py                     # Interfaz Streamlit
├── config.py                  # Configuración centralizada (.env)
├── database.py                # SQLite: persistencia, duplicados y búsqueda
├── extractor.py               # Orquestador de extracción de texto
├── ocr.py                     # Detección de PDFs escaneados y OCR
├── parser.py                  # Texto → campos estructurados (regex)
├── exporter.py                # Exportación a Excel
├── utils.py                   # Logging y funciones de normalización
├── models.py                  # Dataclass Invoice
│
├── invoices/                  # PDFs subidos (no versionado, solo .gitkeep)
├── exports/                   # Archivos Excel generados (no versionado, solo .gitkeep)
├── logs/                      # Logs de la aplicación (no versionado, solo .gitkeep)
│
├── tests/
│   ├── test_utils.py
│   ├── test_parser.py
│   └── test_database.py
│
├── requirements.txt           # Dependencias de producción
├── requirements-dev.txt       # Herramientas de desarrollo (pytest, black, flake8, mypy)
├── .env.example               # Plantilla de configuración
├── .gitignore
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

 Instalación

Requisitos previos


Python 3.11 o superior
Tesseract OCR instalado a nivel de sistema operativo (no se instala vía pip):

Windows: descarga el instalador desde UB-Mannheim/tesseract. Durante la instalación, marca el paquete de idioma español. Anota la ruta de instalación (normalmente C:\Program Files\Tesseract-OCR\tesseract.exe).
Linux (Debian/Ubuntu): sudo apt install tesseract-ocr tesseract-ocr-spa
macOS: brew install tesseract tesseract-lang


## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/invoice-processor.git
cd invoice-processor
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Instalar las dependencias

Para desarrollo (incluye herramientas de testing y calidad de código):

```bash
pip install -r requirements-dev.txt
```

Solo para producción:

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

**Windows**

```bash
copy .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Edita el archivo `.env` y ajusta, especialmente, la ruta al ejecutable de Tesseract:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_LANGUAGE=spa
```

---

## Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en:

```
http://localhost:8501
```

> **Nota:** En la primera ejecución, Streamlit puede solicitar un correo electrónico para su newsletter. Puedes dejarlo en blanco y pulsar **Enter** para continuar.

---

## Flujo de uso

1. Sube uno o varios archivos PDF desde la barra lateral (**📤 Subir facturas**).
2. Pulsa **Procesar facturas**.
3. Cada factura se clasificará como:

| Estado | Significado |
|---------|-------------|
| ✅ **Procesada** | Todos los campos críticos se extrajeron correctamente. |
| ⚠️ **Procesada (incompleta)** | La factura se guardó, pero algunos campos requieren revisión manual. |
| ⚠️ **Duplicada** | Ya existe una factura equivalente en la base de datos. |
| ❌ **Error** | No fue posible procesar el documento. |

4. Utiliza el buscador para filtrar por:
   - Empresa
   - CIF/NIF
   - Número de factura

5. Pulsa **📥 Exportar a Excel** para descargar los resultados (todos o únicamente los filtrados).

---

## Ejecutar los tests

```bash
pytest tests/ -v
```

---

## Detección de duplicados

Una factura se considera duplicada cuando se cumple alguna de las siguientes condiciones:

- Coinciden el **CIF/NIF** y el **número de factura** con una factura ya almacenada.
- Si esos campos no pudieron extraerse, se compara el **hash del texto completo** con el de las facturas existentes. Si coincide, se considera el mismo documento aunque tenga un nombre de archivo diferente.

---

## Limitaciones conocidas

- El parser utiliza expresiones regulares diseñadas para formatos habituales de facturas españolas. Documentos con formatos muy distintos pueden requerir ampliar los patrones definidos en `parser.py`.
- El OCR emplea el modo de segmentación `--psm 6` de Tesseract, adecuado para documentos con una estructura relativamente uniforme. Facturas con diseños muy complejos (múltiples columnas o tablas anidadas) pueden necesitar otra configuración.
- La detección de PDFs escaneados se basa en un umbral mínimo de caracteres (`MIN_TEXT_CHARS_THRESHOLD`), configurable mediante el archivo `.env`.

---

## Futuras mejoras

- Extracción de líneas de detalle (conceptos individuales).
- Panel de estadísticas (gasto por empresa, proveedor o periodo).
- Edición manual de campos incompletos desde la interfaz.
- Exportación a CSV y JSON.
- Soporte para facturas en varios idiomas.
- Dockerfile para facilitar el despliegue.
- Autenticación para múltiples usuarios.

---

## Contribuir

Las pautas de contribución están disponibles en **CONTRIBUTING.md**.

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta **LICENSE** para más información.

---

## Changelog

El historial de versiones puede consultarse en **CHANGELOG.md**.
