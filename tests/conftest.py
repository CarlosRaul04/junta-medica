"""Datos compartidos por todas las pruebas."""
import copy

import pytest

VALID_CASE = {
    "case_id": "CASO-001",
    "age": 68,
    "sex": "M",
    "chief_complaint": "Control de presión arterial",
    "symptoms": ["cefalea", "mareos"],
    "medical_history": ["diabetes mellitus tipo 2"],
    "allergies": ["penicilina"],
    "medications": [{"name": "enalapril", "dose": "10 mg cada 12 h"}, "metformina"],
    "lab_results": {"egfr_ml_min": 55, "potassium_meq_l": 4.6},
}


@pytest.fixture
def valid_case() -> dict:
    """Copia nueva en cada prueba, para poder modificarla sin afectar a otras."""
    return copy.deepcopy(VALID_CASE)


# ---------------------------------------------------------------------------
# Dobles de prueba para el RAG: rápidos, sin descargar modelos.
# ---------------------------------------------------------------------------
import math
import re
import unicodedata
import zlib

from junta_medica.interfaces.vector_store import VectorStore
from junta_medica.interfaces.embedding_model import EmbeddingModel
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk


class FakeEmbeddingModel(EmbeddingModel):
    """Vector = bolsa de palabras (hash en 2048 dimensiones). Textos con palabras en común se parecen."""

    DIMENSIONS = 2048

    def embed_documents(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)

    def _vector(self, text):
        vector = [0.0] * self.DIMENSIONS
        cleaned_text = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
        for word in re.findall(r"[a-z]{4,}", cleaned_text):
            vector[zlib.crc32(word.encode()) % self.DIMENSIONS] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.data = []

    def clear(self):
        self.data = []

    def add(self, chunks, vectors):
        self.data += list(zip(chunks, vectors))

    def search(self, vector, limit, document_ids=None):
        candidates = [(f, v) for f, v in self.data if not document_ids or f.document_id in document_ids]
        scores = [(f, sum(a * b for a, b in zip(vector, v))) for f, v in candidates]
        scores.sort(key=lambda x: -x[1])
        return [RetrievedChunk(f, round(s, 4)) for f, s in scores[:limit]]

    def count(self):
        return len(self.data)


@pytest.fixture
def fake_embeddings():
    return FakeEmbeddingModel()


@pytest.fixture
def in_memory_store():
    return InMemoryVectorStore()
