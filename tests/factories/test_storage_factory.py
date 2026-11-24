"""La fábrica elige SQLite/local o RDS/S3 según STORAGE_BACKEND y avisa si falta configuración."""
import pytest

from junta_medica.config import storage
from junta_medica.exceptions import StorageConfigurationError
from junta_medica.factories import storage_factory
from junta_medica.repositories.storage.local_file_storage import LocalFileStorage
from junta_medica.repositories.users.sqlite_user_store import SQLiteUserStore


@pytest.fixture(autouse=True)
def clean_cache():
    storage_factory.create_database.cache_clear()
    yield
    storage_factory.create_database.cache_clear()


def test_local_backend(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "BACKEND", "local")
    monkeypatch.setattr(storage, "SQLITE_PATH", tmp_path / "x.sqlite")
    assert isinstance(storage_factory.create_user_store(), SQLiteUserStore)
    assert isinstance(storage_factory.create_file_storage(), LocalFileStorage)


@pytest.mark.parametrize("setting", ["MONGODB_URI", "S3_BUCKET"])
def test_aws_backend_requires_its_settings(monkeypatch, setting):
    monkeypatch.setattr(storage, "BACKEND", "aws")
    monkeypatch.setattr(storage, "MONGODB_URI", "")
    monkeypatch.setattr(storage, "S3_BUCKET", "")
    with pytest.raises(StorageConfigurationError, match=setting):
        storage_factory.create_database() if setting == "MONGODB_URI" else storage_factory.create_file_storage()


def test_unknown_backend(monkeypatch):
    monkeypatch.setattr(storage, "BACKEND", "azure")
    with pytest.raises(StorageConfigurationError, match="no existe"):
        storage_factory.create_file_storage()
