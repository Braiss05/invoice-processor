"""Configuración centralizada de la aplicación.

Carga variables de entorno desde el archivo .env y expone constantes
tipadas que el resto de módulos importan. Ningún otro módulo debe
leer os.environ directamente: todo pasa por aquí.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el archivo .env que esté en la raíz del proyecto.
load_dotenv()

# --- Rutas base ---
BASE_DIR: Path = Path(__file__).resolve().parent

INVOICES_DIR: Path = BASE_DIR / os.getenv("INVOICES_DIR", "invoices")
EXPORTS_DIR: Path = BASE_DIR / os.getenv("EXPORTS_DIR", "exports")
LOGS_DIR: Path = BASE_DIR / os.getenv("LOGS_DIR", "logs")

# Nos aseguramos de que las carpetas existen al arrancar la app,
# para no fallar en el primer uso por una carpeta ausente.
for directory in (INVOICES_DIR, EXPORTS_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# --- Base de datos ---
DATABASE_PATH: Path = BASE_DIR / os.getenv("DATABASE_PATH", "invoices.db")

# --- OCR ---
TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "spa")

# --- Heurística texto vs escaneado ---
MIN_TEXT_CHARS_THRESHOLD: int = int(os.getenv("MIN_TEXT_CHARS_THRESHOLD", "50"))

# --- Logging ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE: Path = BASE_DIR / os.getenv("LOG_FILE", "logs/invoice_processor.log")

# --- Negocio ---
DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "EUR")