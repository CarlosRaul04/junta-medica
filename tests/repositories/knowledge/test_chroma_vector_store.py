import pytest

pytest.importorskip("chromadb")

from junta_medica.models.knowledge.chunk import Chunk
from junta_medica.repositories.knowledge.chroma_vector_store import ChromaVectorStore


def chunk(chunk_id, document_id):
    return Chunk(chunk_id, document_id, f"texto {chunk_id}", 10, 11, "recommendations", "Pregunta 1")


def test_adds_searches_filters_and_clears(tmp_path):
    store = ChromaVectorStore(tmp_path / "chroma", "prueba")
    store.add([chunk("a-001", "gpc_a"), chunk("b-001", "gpc_b")], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    assert store.count() == 2

    best = store.search([1.0, 0.1, 0.0], limit=2)[0]
    assert best.chunk.chunk_id == "a-001" and best.similarity > 0.9
    assert best.chunk.citation == "gpc_a:p10-11"

    assert [r.chunk.document_id for r in store.search([1.0, 0.0, 0.0], 2, ["gpc_b"])] == ["gpc_b"]

    store.clear()
    assert store.count() == 0 and store.search([1.0, 0.0, 0.0], 2) == []


def test_persists_between_openings(tmp_path):
    ChromaVectorStore(tmp_path / "chroma", "prueba").add([chunk("a-001", "gpc_a")], [[1.0, 0.0]])
    assert ChromaVectorStore(tmp_path / "chroma", "prueba").count() == 1


def test_old_index_raises_clear_error(tmp_path):
    from junta_medica.exceptions import OutdatedIndexError
    store = ChromaVectorStore(tmp_path / "chroma", "prueba")
    store._collection.add(ids=["x"], embeddings=[[1.0, 0.0]], documents=["texto"],
                          metadatas=[{"documento": "gpc_ic", "pagina_inicio": 1}])
    with pytest.raises(OutdatedIndexError):
        store.search([1.0, 0.0], 1)
