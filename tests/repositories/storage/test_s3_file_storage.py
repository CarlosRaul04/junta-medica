"""S3FileStorage contra un S3 simulado (moto): sin internet ni costo."""
import boto3
import pytest
from moto import mock_aws

from junta_medica.repositories.storage.s3_file_storage import S3FileStorage


@pytest.fixture
def storage(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="junta-medica-test")
        yield S3FileStorage(client, "junta-medica-test"), client


def test_save_and_load(storage):
    files, client = storage
    assert files.save("reports/CASO-008.pdf", b"%PDF-1.4", "application/pdf") == "reports/CASO-008.pdf"
    assert files.load("reports/CASO-008.pdf") == b"%PDF-1.4"
    head = client.head_object(Bucket="junta-medica-test", Key="reports/CASO-008.pdf")
    assert head["ContentType"] == "application/pdf" and head["ServerSideEncryption"] == "AES256"


def test_missing_key_returns_none(storage):
    files, _ = storage
    assert files.load("reports/no-existe.pdf") is None
