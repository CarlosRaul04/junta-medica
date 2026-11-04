"""CitedItem: una afirmación (acción del plan, recomendación, alerta) con las citas que la respaldan."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CitedItem:
    text: str
    citations: tuple[str, ...] = ()   # ej. ("gpc_ic:p22-23", "ft_dabigatran:p84")
