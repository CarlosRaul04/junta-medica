"""Severity de un hallazgo farmacológico (la usan interacciones y reglas fármaco–condición)."""
from enum import Enum


class Severity(str, Enum):
    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"
    UNKNOWN = "unknown"   # la fuente registra el hallazgo pero sin nivel

    @property
    def priority(self) -> int:
        """Mayor número = más grave. Sirve para ordenar y quedarse con la peor severidad."""
        return {"severe": 3, "moderate": 2, "mild": 1, "unknown": 0}[self.value]
