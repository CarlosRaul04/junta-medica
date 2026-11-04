"""KnowledgeRetriever: encuentra los fragmentos de guía más relacionados con una consulta."""
from junta_medica.interfaces.vector_store import VectorStore
from junta_medica.interfaces.embedding_model import EmbeddingModel
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk
from junta_medica.models.knowledge.search_result import SearchResult


class KnowledgeRetriever:
    def __init__(self, embeddings: EmbeddingModel, store: VectorStore, top_k: int, similarity_threshold: float):
        self._embeddings = embeddings
        self._store = store
        self._top_k = top_k
        self._threshold = similarity_threshold

    def search(self, query: str, document_ids: list[str] | None = None,
               limit: int | None = None) -> SearchResult:
        vector = self._embeddings.embed_query(query)
        chunks = self._store.search(vector, limit or self._top_k, document_ids)
        sufficient = bool(chunks) and chunks[0].similarity >= self._threshold
        return SearchResult(query, tuple(chunks), sufficient)

    def search_many(self, queries: list[str], limit: int | None = None,
                    document_ids: list[str] | None = None) -> SearchResult:
        """Varias consultas a la vez: une los fragmentos (sin repetir) y se queda con los más parecidos."""
        best: dict[str, RetrievedChunk] = {}
        for query in queries:
            for retrieved in self.search(query, document_ids, limit).chunks:
                current = best.get(retrieved.chunk.chunk_id)
                if current is None or retrieved.similarity > current.similarity:
                    best[retrieved.chunk.chunk_id] = retrieved
        chunks = sorted(best.values(), key=lambda r: -r.similarity)[: limit or self._top_k]
        sufficient = bool(chunks) and chunks[0].similarity >= self._threshold
        return SearchResult(" | ".join(queries), tuple(chunks), sufficient)
