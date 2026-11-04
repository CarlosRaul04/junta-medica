"""KnowledgeIndexer: arma la base vectorial desde cero con las guías del catálogo."""
from pathlib import Path

from junta_medica.interfaces.vector_store import VectorStore
from junta_medica.interfaces.embedding_model import EmbeddingModel
from junta_medica.models.knowledge.chunk import Chunk
from junta_medica.models.knowledge.indexing_summary import IndexingSummary
from junta_medica.repositories.knowledge.pdf_reader import PDFReader
from junta_medica.repositories.knowledge.document_repository import DocumentRepository
from junta_medica.repositories.knowledge.section_repository import SectionRepository
from junta_medica.services.knowledge.chunker import Chunker
from junta_medica.services.knowledge.text_cleaner import TextCleaner


class KnowledgeIndexer:
    def __init__(self, documents: DocumentRepository, sections: SectionRepository, reader: PDFReader,
                 cleaner: TextCleaner, chunker: Chunker, embeddings: EmbeddingModel,
                 store: VectorStore, documents_folder: Path):
        self._documents = documents
        self._sections = sections
        self._reader = reader
        self._cleaner = cleaner
        self._chunker = chunker
        self._embeddings = embeddings
        self._store = store
        self._folder = documents_folder

    def index(self) -> IndexingSummary:
        self._store.clear()
        summary = {}
        for document in self._documents.indexable():
            if not self._sections.for_document(document.id):
                continue   # sin páginas en sections.csv (ej. fichas técnicas): se consulta, pero no se indexa
            chunks = self._chunk_document(document.id, self._folder / document.file)
            if chunks:
                vectors = self._embeddings.embed_documents([self._text_for_embedding(f) for f in chunks])
                self._store.add(chunks, vectors)
            summary[document.id] = len(chunks)
        return IndexingSummary(summary)

    def _chunk_document(self, document_id: str, path: Path) -> list[Chunk]:
        chunks = []
        for section in self._sections.for_document(document_id):
            pages = self._reader.read_pages(path, document_id, section.start_page, section.end_page)
            chunks += self._chunker.chunk(self._cleaner.clean(pages), section.kind)
        return [self._with_id(f, i) for i, f in enumerate(chunks, start=1)]

    @staticmethod
    def _with_id(chunk: Chunk, number: int) -> Chunk:
        return Chunk(f"{chunk.document_id}-{number:03d}", chunk.document_id, chunk.text,
                         chunk.start_page, chunk.end_page, chunk.section_type, chunk.title)

    @staticmethod
    def _text_for_embedding(chunk: Chunk) -> str:
        return chunk.text
