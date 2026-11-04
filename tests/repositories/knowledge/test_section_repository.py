"""Integridad de data/documents/sections.csv contra el catálogo y los PDF reales."""
import pytest

from junta_medica.config import paths
from junta_medica.repositories.knowledge.pdf_reader import PDFReader
from junta_medica.repositories.knowledge.document_repository import DocumentRepository
from junta_medica.repositories.knowledge.section_repository import SectionRepository

DOCUMENTS = DocumentRepository(paths.CATALOG_PATH)
SECTIONS = SectionRepository(paths.SECTIONS_PATH)


@pytest.mark.parametrize("document", DOCUMENTS.indexable(), ids=lambda d: d.id)
def test_each_downloaded_document_exists(document):
    assert (paths.DOCUMENTS_DIR / document.file).exists()


GUIDELINES = [d for d in DOCUMENTS.indexable() if d.file.startswith("guidelines/")]


@pytest.mark.parametrize("document", GUIDELINES, ids=lambda d: d.id)
def test_each_guideline_has_sections_to_index(document):
    """Las guías se indexan en el RAG. Las fichas técnicas se citan desde las reglas, pero aún no se indexan."""
    assert SECTIONS.for_document(document.id)


@pytest.mark.parametrize("section", SECTIONS.all(), ids=lambda s: f"{s.document_id}-{s.kind}")
def test_valid_page_range(section):
    document = DOCUMENTS.find(section.document_id)
    assert document is not None and document.is_indexable
    total = PDFReader().count_pages(paths.DOCUMENTS_DIR / document.file)
    assert 1 <= section.start_page <= section.end_page <= total
