"""InteractionFinding: una interacción encontrada en la medicación de un caso."""
from dataclasses import dataclass

from junta_medica.models.pharmacology.interaction import Interaction


@dataclass(frozen=True)
class InteractionFinding:
    interaction: Interaction
    highlighted: bool   # RF12: se muestra destacada en el informe
