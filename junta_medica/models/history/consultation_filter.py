"""ConsultationFilter: criterios para buscar en el historial."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultationFilter:
    user_id: int | None = None                  # None = de todos los usuarios (solo administrador)
    text: str = ""                              # busca en código del caso, CIE-10 y diagnóstico
    insufficient_evidence: bool | None = None   # None = todas
    limit: int = 500
