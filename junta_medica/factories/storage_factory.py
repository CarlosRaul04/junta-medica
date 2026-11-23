"""
Arma dónde se guardan usuarios, historial y archivos (config/storage.py).

Hoy: SQLite + carpeta local. En AWS: aquí se devolverán las versiones PostgreSQL (RDS) y S3,
y el resto del sistema no cambia porque depende de las interfaces UserStore, ConsultationStore y FileStorage.
"""
from functools import lru_cache

from junta_medica.config import storage as config
from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.interfaces.file_storage import FileStorage
from junta_medica.interfaces.user_store import UserStore
from junta_medica.repositories.database.sqlite_database import SQLiteDatabase
from junta_medica.repositories.history.sqlite_consultation_store import SQLiteConsultationStore
from junta_medica.repositories.storage.local_file_storage import LocalFileStorage
from junta_medica.repositories.users.sqlite_user_store import SQLiteUserStore


@lru_cache(maxsize=1)
def create_database() -> SQLiteDatabase:
    return SQLiteDatabase(config.SQLITE_PATH)


def create_user_store() -> UserStore:
    return SQLiteUserStore(create_database())


def create_consultation_store() -> ConsultationStore:
    return SQLiteConsultationStore(create_database())


def create_file_storage() -> FileStorage:
    return LocalFileStorage(config.FILES_ROOT)
