import pytest

from junta_medica.exceptions import AccessDeniedError
from junta_medica.factories.history_factory import create_case_id_generator, create_consultation_service
from junta_medica.services.history.csv_exporter import CsvExporter


@pytest.fixture
def service(consultation_store, file_storage):
    return create_consultation_service(consultation_store, file_storage)


@pytest.fixture
def users(auth):
    admin = auth.register("admin", "Ana Pérez", "clave-segura", "clave-segura")
    doctor = auth.register("drlopez", "Luis López", "otra-clave", "otra-clave")
    other = auth.register("drgomez", "Rosa Gómez", "otra-clave", "otra-clave")
    return admin, doctor, other


def test_record_saves_summary_json_and_pdf(service, users, debate_result):
    _, doctor, _ = users
    consultation = service.record(debate_result, doctor)
    assert consultation.case_id == "CASO-008" and consultation.username == "drlopez"
    assert consultation.result_key.startswith("debates/") and consultation.report_key.startswith("reports/")
    result = service.load_result(consultation)
    assert result.case_id == "CASO-008" and result.case["age"] == 77
    assert service.load_report(consultation, "Luis López").startswith(b"%PDF")


def test_physician_sees_only_own_history_and_admin_sees_all(service, users, debate_result):
    admin, doctor, other = users
    mine = service.record(debate_result, doctor)
    service.record(debate_result, other)
    assert [c.consultation_id for c in service.search(doctor, all_users=True)] == [mine.consultation_id]
    assert len(service.search(admin, all_users=True)) == 2
    assert service.get(admin, mine.consultation_id) == mine
    with pytest.raises(AccessDeniedError):
        service.get(other, mine.consultation_id)


def test_search_filters_by_text(service, users, debate_result):
    _, doctor, _ = users
    service.record(debate_result, doctor)
    assert service.search(doctor, text="CASO-008")
    assert not service.search(doctor, text="CASO-999")


def test_case_id_generator_skips_simulated_and_used_codes(service, users, debate_result, consultation_store):
    generator = create_case_id_generator(consultation_store)
    assert generator.next_id() == "CASO-019"          # data/cases tiene CASO-001 a CASO-018


def test_csv_export_has_spanish_headers_and_excel_bom(service, users, debate_result):
    _, doctor, _ = users
    service.record(debate_result, doctor)
    content = CsvExporter().export(service.search(doctor)).decode("utf-8")
    assert content.startswith("﻿N.° consulta,Código del caso")
    assert "CASO-008" in content
