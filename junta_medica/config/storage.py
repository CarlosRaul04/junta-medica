"""
Dónde se guardan el historial (base de datos) y los archivos (resultados JSON, informes PDF).

Hoy: SQLite + carpeta local. En la nube (AWS) se cambiará por PostgreSQL en RDS + un bucket S3;
solo cambian las fábricas (factories/storage_factory.py), no la interfaz ni los servicios.
"""
from junta_medica.config.paths import DATABASE_PATH, OUTPUT_DIR

SQLITE_PATH = DATABASE_PATH
FILES_ROOT = OUTPUT_DIR           # las claves quedan como "debates/..." y "reports/..."
RESULTS_PREFIX = "debates"
REPORTS_PREFIX = "reports"
JSON_CONTENT_TYPE = "application/json"
PDF_CONTENT_TYPE = "application/pdf"
