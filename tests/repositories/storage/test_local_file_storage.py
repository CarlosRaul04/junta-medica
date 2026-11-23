import pytest

from junta_medica.repositories.storage.local_file_storage import LocalFileStorage


def test_save_and_load(tmp_path):
    storage = LocalFileStorage(tmp_path)
    assert storage.save("reports/a.pdf", b"%PDF", "application/pdf") == "reports/a.pdf"
    assert storage.load("reports/a.pdf") == b"%PDF"
    assert storage.load("reports/no-existe.pdf") is None


def test_keys_cannot_escape_the_folder(tmp_path):
    with pytest.raises(ValueError):
        LocalFileStorage(tmp_path / "files").save("../fuera.txt", b"x", "text/plain")
