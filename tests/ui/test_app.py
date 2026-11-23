"""Prueba de humo de la interfaz (Streamlit AppTest): crear la primera cuenta y entrar al inicio."""
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from junta_medica.config import paths, storage
from junta_medica.factories import storage_factory


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SQLITE_PATH", tmp_path / "app.sqlite")
    monkeypatch.setattr(storage, "FILES_ROOT", tmp_path / "files")
    storage_factory.create_database.cache_clear()
    st.cache_resource.clear()      # los servicios se crean de nuevo con la base temporal
    test = AppTest.from_file(str(paths.ROOT_DIR / "app.py"), default_timeout=30)
    test.run()
    yield test
    storage_factory.create_database.cache_clear()


def test_first_visit_asks_for_the_admin_account(app):
    assert not app.exception
    assert any("administrador" in b.label for b in app.button)


def test_register_admin_and_land_on_home(app):
    app.text_input[0].input("Dra. Ana Pérez")
    app.text_input[1].input("aperez")
    app.text_input[2].input("clave-segura")
    app.text_input[3].input("clave-segura")
    next(b for b in app.button if "administrador" in b.label).click().run()
    assert not app.exception
    assert any("Hola, Ana" in m.value for m in app.markdown)


def test_password_mismatch_shows_spanish_error(app):
    app.text_input[0].input("Ana")
    app.text_input[1].input("aperez")
    app.text_input[2].input("clave-segura")
    app.text_input[3].input("otra-clave")
    next(b for b in app.button if "administrador" in b.label).click().run()
    assert any("no coinciden" in e.value for e in app.error)
