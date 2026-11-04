"""FinalAlert: una alerta que va al informe. Las de la tabla (sin IA) siempre se incluyen."""
from dataclasses import dataclass

from junta_medica.models.pharmacology.severity import Severity


@dataclass(frozen=True)
class FinalAlert:
    text: str
    severity: Severity
    citations: tuple[str, ...]
    origin: str                    # "interaction_table" | "condition_rules" | "agent"
    highlighted: bool              # RF12: alerta destacada
