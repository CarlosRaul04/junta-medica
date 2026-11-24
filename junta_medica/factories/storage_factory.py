"""
Arma dónde se guardan usuarios, historial y archivos según STORAGE_BACKEND (config/storage.py):

    local -> SQLite + carpeta output/
    aws   -> MongoDB + bucket S3

El resto del sistema depende solo de las interfaces UserStore, ConsultationStore y FileStorage.
"""
from functools import lru_cache

from junta_medica.config import storage as config
from junta_medica.exceptions import StorageConfigurationError
from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.interfaces.file_storage import FileStorage
from junta_medica.interfaces.user_store import UserStore
from junta_medica.repositories.database.sqlite_database import SQLiteDatabase
from junta_medica.repositories.history.sqlite_consultation_store import SQLiteConsultationStore
from junta_medica.repositories.storage.local_file_storage import LocalFileStorage
from junta_medica.repositories.users.sqlite_user_store import SQLiteUserStore


def _check_backend() -> str:
    if config.BACKEND not in (config.LOCAL_BACKEND, config.AWS_BACKEND):
        raise StorageConfigurationError(
            f"STORAGE_BACKEND={config.BACKEND!r} no existe. Usa '{config.LOCAL_BACKEND}' o '{config.AWS_BACKEND}'.")
    return config.BACKEND


@lru_cache(maxsize=1)
def create_database():
    if _check_backend() == config.AWS_BACKEND:
        if not config.MONGODB_URI:
            raise StorageConfigurationError("Con STORAGE_BACKEND=aws hay que poner MONGODB_URI en el .env.")
        from pymongo import MongoClient
        from junta_medica.repositories.database.mongo_database import MongoDatabase
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=config.DATABASE_TIMEOUT_MS)
        return MongoDatabase(client, config.MONGODB_DATABASE)
    return SQLiteDatabase(config.SQLITE_PATH)


def create_user_store() -> UserStore:
    database = create_database()
    if config.BACKEND == config.AWS_BACKEND:
        from junta_medica.repositories.users.mongo_user_store import MongoUserStore
        return MongoUserStore(database)
    return SQLiteUserStore(database)


def create_consultation_store() -> ConsultationStore:
    database = create_database()
    if config.BACKEND == config.AWS_BACKEND:
        from junta_medica.repositories.history.mongo_consultation_store import MongoConsultationStore
        return MongoConsultationStore(database)
    return SQLiteConsultationStore(database)


def create_file_storage() -> FileStorage:
    if _check_backend() == config.AWS_BACKEND:
        if not config.S3_BUCKET:
            raise StorageConfigurationError("Con STORAGE_BACKEND=aws hay que poner S3_BUCKET en el .env.")
        import boto3
        from junta_medica.repositories.storage.s3_file_storage import S3FileStorage
        return S3FileStorage(boto3.client("s3", region_name=config.AWS_REGION), config.S3_BUCKET)
    return LocalFileStorage(config.FILES_ROOT)
