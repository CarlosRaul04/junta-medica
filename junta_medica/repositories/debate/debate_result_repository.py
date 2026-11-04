"""
DebateResultRepository: guarda el resultado completo de un caso como JSON (output/debates/CASO-XXX_<fecha>.json).

Incluye cada intervención con su JSON original, modelo, tokens, costo y tiempo (trazabilidad por agente, RF14).
Lo usarán la evaluación (Fase 5) y, más adelante, el historial.
"""
import dataclasses
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from junta_medica.models.debate.debate_result import DebateResult


class DebateResultRepository:
    def __init__(self, folder: Path, embedding_model: str):
        self._folder = folder
        self._embedding_model = embedding_model

    def save(self, result: DebateResult) -> Path:
        self._folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self._folder / f"{result.case_id}_{stamp}.json"
        path.write_text(json.dumps(self.to_dict(result), ensure_ascii=False, indent=2, default=self._default),
                        encoding="utf-8")
        return path

    def to_dict(self, result: DebateResult) -> dict:
        data = dataclasses.asdict(result)
        data["summary"] = {
            "abstained": result.abstained,
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

    @staticmethod
    def _default(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (set, frozenset)):
            return sorted(value)
        raise TypeError(f"No se puede guardar como JSON: {type(value).__name__}")
