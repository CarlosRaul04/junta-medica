"""
DebateResultRepository: guarda el resultado completo de un caso como JSON (output/debates/CASO-XXX_<fecha>.json).

Incluye cada intervención con su JSON original, modelo, tokens, costo y tiempo (trazabilidad por agente, RF14).
Lo usa la terminal (scripts/run_case.py). La interfaz web guarda lo mismo a través de ConsultationService.
"""
from datetime import datetime
from pathlib import Path

from junta_medica.models.debate.debate_result import DebateResult
from junta_medica.repositories.debate.debate_result_serializer import DebateResultSerializer


class DebateResultRepository:
    def __init__(self, folder: Path, serializer: DebateResultSerializer):
        self._folder = folder
        self._serializer = serializer

    def save(self, result: DebateResult) -> Path:
        self._folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self._folder / f"{result.case_id}_{stamp}.json"
        path.write_text(self._serializer.to_json(result), encoding="utf-8")
        return path

    def to_dict(self, result: DebateResult) -> dict:
        return self._serializer.to_dict(result)
