"""ChromaVectorStore: base vectorial persistente con ChromaDB (carpeta chroma_db/)."""
from pathlib import Path

from junta_medica.exceptions import OutdatedIndexError
from junta_medica.interfaces.vector_store import VectorStore
from junta_medica.models.knowledge.chunk import Chunk
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk


class ChromaVectorStore(VectorStore):
    REQUIRED_METADATA = ("document_id", "start_page", "end_page", "section_type")

    def __init__(self, folder: Path, collection_name: str):
        import chromadb  # se importa aquí para no exigir la librería a quien no usa la base vectorial
        self._client = chromadb.PersistentClient(path=str(folder))
        self._name = collection_name
        self._collection = self._get_collection()

    def _get_collection(self):
        # similitud coseno; los vectores los calculamos nosotros (sin función de embeddings de Chroma)
        return self._client.get_or_create_collection(
            name=self._name, embedding_function=None, metadata={"hnsw:space": "cosine"},
        )

    def clear(self) -> None:
        self._client.delete_collection(self._name)
        self._collection = self._get_collection()

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if not chunks:
            return
        self._collection.add(
            ids=[f.chunk_id for f in chunks],
            embeddings=vectors,
            documents=[f.text for f in chunks],
            metadatas=[{
                "document_id": f.document_id, "start_page": f.start_page, "end_page": f.end_page,
                "section_type": f.section_type, "title": f.title,
            } for f in chunks],
        )

    def search(self, vector: list[float], limit: int,
               document_ids: list[str] | None = None) -> list[RetrievedChunk]:
        if self.count() == 0:
            return []
        where_filter = {"document_id": {"$in": document_ids}} if document_ids else None
        response = self._collection.query(
            query_embeddings=[vector], n_results=min(limit, self.count()), where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
        if any(key not in meta for meta in response["metadatas"][0] for key in self.REQUIRED_METADATA):
            raise OutdatedIndexError()
        retrieved_chunks = []
        for chunk_id, text, meta, distance in zip(
            response["ids"][0], response["documents"][0], response["metadatas"][0], response["distances"][0]
        ):
            chunk = Chunk(chunk_id, meta["document_id"], text, int(meta["start_page"]),
                                  int(meta["end_page"]), meta["section_type"], meta.get("title", ""))
            retrieved_chunks.append(RetrievedChunk(chunk, round(1 - distance, 4)))  # distancia coseno -> similitud
        return retrieved_chunks

    def count(self) -> int:
        return self._collection.count()
