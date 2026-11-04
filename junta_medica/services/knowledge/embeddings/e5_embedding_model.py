"""
E5EmbeddingModel: embeddings con intfloat/multilingual-e5 (sentence-transformers), en la CPU, gratis.

Los modelos e5 esperan prefijos: "passage: " para los documentos y "query: " para las consultas.
La primera vez descarga el modelo (~470 MB) y queda guardado en la caché de Hugging Face.
"""
from junta_medica.interfaces.embedding_model import EmbeddingModel


class E5EmbeddingModel(EmbeddingModel):
    def __init__(self, model_name: str, batch_size: int):
        self._name = model_name
        self._batch_size = batch_size
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # pesado: se carga solo si se usa
            self._model = SentenceTransformer(self._name)
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed([f"passage: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._embed([f"query: {text}"])[0]

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._get_model().encode(texts, batch_size=self._batch_size, normalize_embeddings=True)
        return [v.tolist() for v in vectors]
