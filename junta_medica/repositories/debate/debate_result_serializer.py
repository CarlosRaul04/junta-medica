"""
DebateResultSerializer: convierte el resultado de un caso en un diccionario / JSON.

Ese JSON es el formato común: se guarda en output/debates/ (terminal), en el almacenamiento de archivos
(interfaz web; luego S3) y lo leen el historial, el informe PDF y la evaluación.
"""
import dataclasses
import json
from enum import Enum

from junta_medica.models.debate.debate_result import DebateResult


class DebateResultSerializer:
    def __init__(self, embedding_model: str):
        self._embedding_model = embedding_model

    def to_dict(self, result: DebateResult) -> dict:
        data = json.loads(json.dumps(dataclasses.asdict(result), default=self._default))
        data["summary"] = {
            "abstained": result.abstained,
            "insufficient_evidence": result.insufficient_evidence,
            "rounds": len(result.rounds),
            "final_agreement": result.final_agreement,
            "llm_calls": result.llm_calls,
            "cost_usd": round(result.cost_usd, 6),
            "seconds": round(result.seconds, 2),
            "traceability": round(result.citation_check.traceability, 3),
            "invalid_citations": list(result.citation_check.invalid),
            "models": sorted({t.llm.model for t in result.turns}),
            "embedding_model": self._embedding_model,
        }
        return data

    def to_json(self, result: DebateResult) -> str:
        return json.dumps(self.to_dict(result), ensure_ascii=False, indent=2)

    @staticmethod
    def _default(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (set, frozenset)):
            return sorted(value)
        raise TypeError(f"No se puede guardar como JSON: {type(value).__name__}")
