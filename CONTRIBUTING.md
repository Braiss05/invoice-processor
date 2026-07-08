# Contribuir a Invoice Processor

Gracias por tu interés en contribuir. Estas son las pautas para colaborar con el proyecto.

## Cómo reportar un error

Abre un Issue e incluye:

- Descripción del problema y comportamiento esperado.
- Pasos para reproducirlo.
- Si es posible, un PDF de ejemplo (sin datos sensibles) que provoque el fallo.
- El mensaje de error o traza del log (logs/invoice_processor.log).

## Cómo proponer una mejora

Abre un Issue describiendo:

- Qué problema resuelve la mejora.
- Cómo se comportaría la aplicación con el cambio propuesto.

## Flujo de trabajo para contribuir código

1. Haz un fork del repositorio y clónalo localmente.
2. Crea una rama descriptiva a partir de main:

   git checkout -b feature/nombre-de-la-mejora
   # o
   git checkout -b fix/nombre-del-bug

3. Instala las dependencias de desarrollo:

   pip install -r requirements-dev.txt

4. Realiza tus cambios siguiendo el estilo del proyecto (ver más abajo).
5. Asegúrate de que todos los tests pasan antes de subir tu cambio:

   pytest tests/ -v

6. Si añades una funcionalidad nueva, añade también sus tests correspondientes en tests/.
7. Haz commit siguiendo la convención de mensajes (ver más abajo).
8. Abre un Pull Request contra main, describiendo qué cambia y por qué.

## Estilo de código

El proyecto sigue Clean Code y PEP8:

- Type hints en todas las funciones públicas.
- Docstrings (estilo Google) en todos los módulos, clases y funciones.
- Logging en vez de print() para cualquier mensaje de diagnóstico.
- Formateo con black y comprobación de estilo con flake8:

  black .
  flake8 .

- Comprobación de tipos con mypy (opcional pero recomendado):

  mypy .

## Convención de mensajes de commit

Este proyecto usa Conventional Commits:

| Prefijo    | Uso                                                          |
|------------|---------------------------------------------------------------|
| feat:      | Nueva funcionalidad                                          |
| fix:       | Corrección de un error                                        |
| docs:      | Cambios solo en documentación                                 |
| test:      | Añadir o modificar tests                                      |
| refactor:  | Cambio de código que no añade funcionalidad ni corrige errores |
| chore:     | Mantenimiento (dependencias, configuración, etc.)              |

Ejemplo:

fix: corregir extracción de número de factura y orden de lectura OCR

## Estructura del proyecto

Antes de contribuir, es útil entender la separación de responsabilidades entre módulos — está detallada en la sección "Arquitectura" del README.md. En resumen: cada módulo tiene una única responsabilidad (extracción, parseo, persistencia, exportación, presentación), y las nuevas contribuciones deben respetar esa separación en vez de mezclar lógica entre capas.

## Código de conducta

Sé respetuoso y constructivo en issues y pull requests. Este es un proyecto de aprendizaje y portfolio abierto a sugerencias de cualquier nivel de experiencia.