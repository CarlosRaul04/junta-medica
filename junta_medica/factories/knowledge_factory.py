"""Arma el indexador y el buscador de la base de conocimiento (RAG)."""
from junta_medica.config import knowledge as config
from junta_medica.config import paths
from junta_medica.interfaces.vector_store import VectorStore
from junta_medica.interfaces.embedding_model import EmbeddingModel
from junta_medica.repositories.knowledge.chroma_vector_store import ChromaVectorStore
from junta_medica.repositories.knowledge.pdf_reader import PDFReader
from junta_medica.repositories.knowledge.document_repository import DocumentRepository
from junta_medica.repositories.knowledge.section_repository import SectionRepository
from junta_medica.services.knowledge.retriever import KnowledgeRetriever
from junta_medica.services.knowledge.embeddings.e5_embedding_model import E5EmbeddingModel
from junta_medica.services.knowledge.chunker import Chunker
from junta_medica.services.knowledge.indexer import KnowledgeIndexer
from junta_medica.services.knowledge.text_cleaner import TextCleaner


def create_embedding_model() -> EmbeddingModel:
    return E5EmbeddingModel(config.EMBEDDING_MODEL, config.EMBEDDING_BATCH_SIZE)


def create_vector_store() -> VectorStore:
    return ChromaVectorStore(paths.CHROMA_DIR, config.COLLECTION_NAME)


def create_chunker() -> Chunker:
    return Chunker(config.BLOCK_START_PATTERN, config.MAX_CHUNK_SIZE,
                        config.CHUNK_OVERLAP, config.MIN_CHUNK_SIZE)


def create_text_cleaner() -> TextCleaner:
    return TextCleaner(config.LINE_PATTERNS_TO_REMOVE, config.HEADER_RATIO, config.EDGE_LINES)


def create_indexer(embeddings: EmbeddingModel | None = None,
                    store: VectorStore | None = None) -> KnowledgeIndexer:
    return KnowledgeIndexer(
        documents=DocumentRepository(paths.CATALOG_PATH),
        sections=SectionRepository(paths.SECTIONS_PATH),
        reader=PDFReader(),
        cleaner=create_text_cleaner(),
        chunker=create_chunker(),
        embeddings=embeddings or create_embedding_model(),
        store=store or create_vector_store(),
        documents_folder=paths.DOCUMENTS_DIR,
    )


def create_retriever(embeddings: EmbeddingModel | None = None,
                   store: VectorStore | None = None) -> KnowledgeRetriever:
    return KnowledgeRetriever(embeddings or create_embedding_model(), store or create_vector_store(),
                                config.TOP_K, config.MIN_SIMILARITY)
