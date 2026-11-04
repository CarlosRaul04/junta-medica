"""
Prueba rápida del buscador desde la terminal.

Uso:  python -m scripts.search_guidelines "metformina en enfermedad renal"
"""
import sys

from junta_medica.exceptions import OutdatedIndexError
from junta_medica.factories.knowledge_factory import create_retriever


def main() -> None:
    query = " ".join(sys.argv[1:]) or "dosis de espironolactona en insuficiencia cardiaca"
    try:
        result = create_retriever().search(query)
    except OutdatedIndexError as error:
        sys.exit(str(error))
    print(f'Consulta: "{query}"  ->  evidencia suficiente: {"sí" if result.sufficient_evidence else "NO"}\n')
    for i, retrieved in enumerate(result.chunks, start=1):
        f = retrieved.chunk
        print(f"{i}. [{f.citation}] similitud {retrieved.similarity:.3f} · {f.title[:90]}")
        print("   " + f.text[:300].replace("\n", " ") + "...\n")


if __name__ == "__main__":
    main()
