"""Arma el formateador de citas y el generador del informe PDF."""
from junta_medica.config import cases as cases_config
from junta_medica.config import paths, texts
from junta_medica.repositories.knowledge.document_repository import DocumentRepository
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.date_formatter import DateFormatter
from junta_medica.services.reports.pdf_report_builder import PdfReportBuilder


def create_citation_formatter() -> CitationFormatter:
    return CitationFormatter(DocumentRepository(paths.CATALOG_PATH).all(), texts.EXTERNAL_SOURCES)


def create_date_formatter() -> DateFormatter:
    return DateFormatter(texts.DISPLAY_TIMEZONE)


def create_pdf_report_builder(citations: CitationFormatter | None = None) -> PdfReportBuilder:
    labels = {"severity": texts.SEVERITY_LABELS, "stance": texts.STANCE_LABELS, "role": texts.ROLE_LABELS,
              "sex": texts.SEX_LABELS, "likelihood": texts.LIKELIHOOD_LABELS}
    return PdfReportBuilder(citations or create_citation_formatter(), create_date_formatter(), labels,
                            cases_config.RECOGNIZED_LAB_TESTS, texts.DISCLAIMER, texts.REPORT_TITLE)
