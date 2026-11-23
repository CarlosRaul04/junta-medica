"""Arma los servicios del historial de consultas (RF16)."""
from junta_medica.config import cases as cases_config
from junta_medica.config import storage as config
from junta_medica.config import texts
from junta_medica.factories.debate_factory import create_debate_result_serializer
from junta_medica.factories.report_factory import create_pdf_report_builder
from junta_medica.factories.storage_factory import create_consultation_store, create_file_storage
from junta_medica.factories.case_factory import create_case_repository
from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.interfaces.file_storage import FileStorage
from junta_medica.services.history.case_id_generator import CaseIdGenerator
from junta_medica.services.history.consultation_service import ConsultationService
from junta_medica.services.history.csv_exporter import CsvExporter


def create_consultation_service(store: ConsultationStore | None = None,
                                files: FileStorage | None = None) -> ConsultationService:
    return ConsultationService(
        store or create_consultation_store(), files or create_file_storage(), create_debate_result_serializer(),
        create_pdf_report_builder(), config.RESULTS_PREFIX, config.REPORTS_PREFIX,
        config.JSON_CONTENT_TYPE, config.PDF_CONTENT_TYPE, texts.INSUFFICIENT_EVIDENCE_LABEL,
    )


def create_case_id_generator(store: ConsultationStore | None = None) -> CaseIdGenerator:
    return CaseIdGenerator(store or create_consultation_store(), create_case_repository().list_ids(),
                           cases_config.CASE_ID_PREFIX, cases_config.CASE_ID_DIGITS)


def create_csv_exporter() -> CsvExporter:
    return CsvExporter()
