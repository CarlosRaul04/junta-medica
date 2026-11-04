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
