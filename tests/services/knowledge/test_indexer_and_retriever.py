"""Indexa las guías REALES (texto de los PDF) con embeddings falsos y prueba la búsqueda de punta a punta."""
import pytest

from junta_medica.factories.knowledge_factory import create_retriever, create_indexer
from junta_medica.services.knowledge.retriever import KnowledgeRetriever


@pytest.fixture(scope="module")
def indexed_base():
    from conftest import InMemoryVectorStore, FakeEmbeddingModel
    embeddings, store = FakeEmbeddingModel(), InMemoryVectorStore()
    summary = create_indexer(embeddings, store).index()
    return summary, embeddings, store


def test_indexes_the_six_guidelines(indexed_base):
    summary, _, store = indexed_base
    assert set(summary.chunks_by_document) == {"gpc_hta", "gpc_dm2", "gpc_ic", "gpc_fa", "gpc_erc", "gpc_nac"}
    assert all(limit > 5 for limit in summary.chunks_by_document.values())
    assert store.count() == summary.total_chunks


def test_unique_ids_and_citations_with_page(indexed_base):
    _, _, store = indexed_base
    ids = [f.chunk_id for f, _ in store.data]
    assert len(ids) == len(set(ids))
    assert all(f.citation.startswith(f"{f.document_id}:p") for f, _ in store.data)


@pytest.mark.parametrize("query, document", [
    ("espironolactona potasio insuficiencia cardiaca fraccion eyeccion", "gpc_ic"),
    ("metformina sulfonilureas hemoglobina glicosilada diabetes", "gpc_dm2"),
    ("anticoagulacion warfarina fibrilacion auricular", "gpc_fa"),
    ("antibiotico amoxicilina neumonia comunidad", "gpc_nac"),
])
def test_search_finds_the_right_guideline(indexed_base, query, document):
    """Con embeddings falsos (solo palabras en común) se exige la guía correcta entre los 3 primeros.
    La calidad real se mide con el modelo e5: python -m scripts.search_guidelines "..." """
    _, embeddings, store = indexed_base
    result = create_retriever(embeddings, store).search(query)
    assert document in [f.chunk.document_id for f in result.chunks[:3]]


def test_filter_by_document(indexed_base):
    _, embeddings, store = indexed_base
    result = create_retriever(embeddings, store).search("dose", document_ids=["gpc_erc"])
    assert {f.chunk.document_id for f in result.chunks} == {"gpc_erc"}


def test_insufficient_evidence_when_similarity_is_low(indexed_base):
    _, embeddings, store = indexed_base
    strict_retriever = KnowledgeRetriever(embeddings, store, top_k=3, similarity_threshold=0.99)
    assert not strict_retriever.search("tratamiento de la psoriasis en placas").sufficient_evidence
