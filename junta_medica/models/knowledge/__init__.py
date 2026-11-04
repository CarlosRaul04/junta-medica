"""
Modelos de la base de conocimiento (RAG):
    source_document.py     -> SourceDocument (una guía registrada en catalog.csv)
    document_section.py    -> DocumentSection (rango de páginas que se indexa)
    page_text.py         -> PageText (texto extraído de una página del PDF)
    chunk.py            -> Chunk (trozo de guía que se indexa y se cita)
    retrieved_chunk.py -> RetrievedChunk (fragmento encontrado + su similitud)
    search_result.py   -> SearchResult (lo que devuelve una búsqueda)
    indexing_summary.py   -> IndexingSummary (cuánto se indexó)
"""
