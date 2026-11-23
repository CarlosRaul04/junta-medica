from junta_medica.factories.knowledge_factory import create_indexer
from junta_medica.services.knowledge.retriever import KnowledgeRetriever


def test_search_many_merges_without_duplicates(fake_embeddings, in_memory_store):
    create_indexer(fake_embeddings, in_memory_store).index()
    retriever = KnowledgeRetriever(fake_embeddings, in_memory_store, 5, 0.05)
    result = retriever.search_many(["metformina enfermedad renal", "metformina enfermedad renal", "neumonía"], 6)
    ids = [r.chunk.chunk_id for r in result.chunks]
    assert len(ids) == len(set(ids)) <= 6
    similarities = [r.similarity for r in result.chunks]
    assert similarities == sorted(similarities, reverse=True)


def test_complement_adds_fragments_but_keeps_the_decisive_evidence(fake_embeddings, in_memory_store):
    """Un medicamento mencionado en una guía no debe hacer "suficiente" un caso que la guía no cubre."""
    from junta_medica.models.knowledge.search_result import SearchResult
    create_indexer(fake_embeddings, in_memory_store).index()
    retriever = KnowledgeRetriever(fake_embeddings, in_memory_store, 5, 0.05)
    decisive = SearchResult("psoriasis", (), False)
    extra = retriever.search_many(["hidrocortisona corticoide neumonía"], 3)
    combined = retriever.complement(decisive, extra, 5)
    assert combined.chunks and combined.sufficient_evidence is False
