"""
Las mismas pruebas para SQLite (local) y MongoDB (AWS): ambas versiones deben comportarse igual.

MongoDB se prueba con un MongoDB simulado en memoria (mongomock). Para probar contra un MongoDB real
(ej. el del servidor), definir TEST_MONGODB_URI=mongodb://localhost:27017 (usa la base junta_medica_test).
"""
import os

import mongomock
import pytest
from pymongo import MongoClient

from junta_medica.models.history.consultation_filter import ConsultationFilter
from junta_medica.models.history.new_consultation import NewConsultation
from junta_medica.models.users.role import Role
from junta_medica.repositories.database.sqlite_database import SQLiteDatabase
from junta_medica.repositories.history.sqlite_consultation_store import SQLiteConsultationStore
from junta_medica.repositories.users.sqlite_user_store import SQLiteUserStore

MONGODB_URI = os.getenv("TEST_MONGODB_URI", "")


def _mongo_stores(client):
    from junta_medica.repositories.database.mongo_database import MongoDatabase
    from junta_medica.repositories.history.mongo_consultation_store import MongoConsultationStore
    from junta_medica.repositories.users.mongo_user_store import MongoUserStore
    for collection in client["junta_medica_test"].list_collection_names():   # basta el permiso readWrite
        client["junta_medica_test"].drop_collection(collection)
    database = MongoDatabase(client, "junta_medica_test")
    return MongoUserStore(database), MongoConsultationStore(database)


@pytest.fixture(params=["sqlite", "mongo_simulated", pytest.param("mongo_real", marks=pytest.mark.skipif(
    not MONGODB_URI, reason="sin TEST_MONGODB_URI (MongoDB real de pruebas)"))])
def stores(request, tmp_path):
    if request.param == "mongo_simulated":
        return _mongo_stores(mongomock.MongoClient())
    if request.param == "mongo_real":
        return _mongo_stores(MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000))
    database = SQLiteDatabase(tmp_path / "contract.sqlite")
    return SQLiteUserStore(database), SQLiteConsultationStore(database)


def _consultation(user_id: int, case_id: str, insufficient: bool = False) -> NewConsultation:
    return NewConsultation(case_id=case_id, user_id=user_id, insufficient_evidence=insufficient,
                           primary_icd10="" if insufficient else "E87.5",
                           primary_name="Evidencia insuficiente" if insufficient else "Hiperpotasemia",
                           agreement=0.67, rounds=2, severe_alerts=1, traceability=0.9, seconds=95.5,
                           llm_calls=7, models="m", result_key=f"debates/{case_id}.json")


def test_users_roundtrip(stores):
    users, _ = stores
    assert users.count() == 0
    admin = users.add("admin", "Ana", "hash-1", Role.ADMIN)
    doctor = users.add("drlopez", "Luis", "hash-2", Role.PHYSICIAN)
    found, password_hash = users.find_with_hash("drlopez")
    assert found == doctor and password_hash == "hash-2"
    assert users.find_with_hash("nadie") is None
    users.update_role(doctor.user_id, Role.ADMIN)
    users.set_active(doctor.user_id, False)
    stored = {u.username: u for u in users.all()}
    assert stored["drlopez"].role is Role.ADMIN and not stored["drlopez"].active
    assert stored["admin"] == admin and users.count() == 2


def test_consultations_add_get_search_and_report_key(stores):
    users, consultations = stores
    ana = users.add("ana", "Ana", "h", Role.ADMIN)
    luis = users.add("luis", "Luis", "h", Role.PHYSICIAN)
    first = consultations.add(_consultation(ana.user_id, "CASO-008"))
    second = consultations.add(_consultation(luis.user_id, "CASO-017", insufficient=True))
    assert first.username == "ana" and first.agreement == 0.67 and first.report_key == ""
    consultations.set_report_key(first.consultation_id, "reports/CASO-008.pdf")
    assert consultations.get(first.consultation_id).report_key == "reports/CASO-008.pdf"
    assert consultations.get(9999) is None
    assert [c.case_id for c in consultations.search(ConsultationFilter())] == ["CASO-017", "CASO-008"]
    assert [c.case_id for c in consultations.search(ConsultationFilter(user_id=luis.user_id))] == ["CASO-017"]
    assert [c.case_id for c in consultations.search(ConsultationFilter(text="e87"))] == ["CASO-008"]
    assert [c.case_id for c in consultations.search(ConsultationFilter(insufficient_evidence=True))] == ["CASO-017"]
    assert second.insufficient_evidence is True


def test_duplicate_username_is_rejected_by_the_database(stores):
    users, _ = stores
    users.add("ana", "Ana", "h", Role.ADMIN)
    with pytest.raises(Exception):
        users.add("ana", "Otra Ana", "h", Role.PHYSICIAN)
