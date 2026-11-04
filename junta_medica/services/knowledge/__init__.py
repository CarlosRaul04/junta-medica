"""
Servicios de la base de conocimiento (RAG):
    text_cleaner.py -> TextCleaner: quita encabezados, pies, números de página y firmas digitales
    chunker.py    -> Chunker: parte el texto en bloques (una pregunta clínica = un bloque)
    indexer.py       -> KnowledgeIndexer: PDF -> texto -> fragmentos -> vectores -> base vectorial
    retriever.py        -> KnowledgeRetriever: consulta -> fragmentos más parecidos (+ ¿evidencia suficiente?)
    embeddings/        -> E5EmbeddingModel (multilingual-e5, local)
"""
