"""CitationCheck: resultado de revisar que cada cita de los agentes exista en lo que se les entregó."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CitationCheck:
    valid: tuple[str, ...]
    invalid: tuple[str, ...]         # citas inventadas o mal escritas
    cited_claims: int                # afirmaciones con al menos una cita válida
    total_claims: int

    @property
    def traceability(self) -> float:
        """Proporción de afirmaciones respaldadas por al menos una cita válida (meta del documento: >= 90 %)."""
        return self.cited_claims / self.total_claims if self.total_claims else 1.0
