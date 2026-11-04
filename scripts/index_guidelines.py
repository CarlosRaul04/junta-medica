"""
Construye (o reconstruye) la base vectorial con las guías del catálogo.

Uso:  python -m scripts.index_guidelines
La primera vez descarga el modelo de embeddings (~470 MB). Luego tarda 1–3 minutos.
"""
import time

from junta_medica.config import paths
from junta_medica.factories.knowledge_factory import create_indexer


def main() -> None:
    start = time.perf_counter()
    summary = create_indexer().index()
    for document_id, limit in summary.chunks_by_document.items():
        print(f"  {document_id}: {limit} fragmentos")
    print(f"Total: {summary.total_chunks} fragmentos en {time.perf_counter() - start:.0f} s")
    print(f"Base vectorial guardada en: {paths.CHROMA_DIR}")


if __name__ == "__main__":
    main()
