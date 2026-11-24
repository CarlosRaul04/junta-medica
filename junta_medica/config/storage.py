"""
Dónde se guardan el historial (base de datos) y los archivos (resultados JSON, informes PDF).

STORAGE_BACKEND (en el .env):
    local -> SQLite (junta_medica.sqlite) + carpeta output/          (por defecto, sin internet)
    aws   -> MongoDB (MONGODB_URI, en el servidor EC2 de AWS) + bucket S3 (S3_BUCKET)
Solo cambian las fábricas (factories/storage_factory.py): la interfaz y los servicios son los mismos.
"""
from junta_medica.config import environment
from junta_medica.config.paths import DATABASE_PATH, OUTPUT_DIR

LOCAL_BACKEND = "local"
AWS_BACKEND = "aws"
BACKEND = environment.STORAGE_BACKEND
MONGODB_URI = environment.MONGODB_URI
MONGODB_DATABASE = environment.MONGODB_DATABASE
S3_BUCKET = environment.S3_BUCKET
AWS_REGION = environment.AWS_REGION
DATABASE_TIMEOUT_MS = 10_000      # si MongoDB no responde en 10 s, error claro (no esperar para siempre)

SQLITE_PATH = DATABASE_PATH
FILES_ROOT = OUTPUT_DIR           # las claves quedan como "debates/..." y "reports/..."
RESULTS_PREFIX = "debates"
REPORTS_PREFIX = "reports"
JSON_CONTENT_TYPE = "application/json"
PDF_CONTENT_TYPE = "application/pdf"
