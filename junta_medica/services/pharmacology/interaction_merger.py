"""Une varias listas de interacciones (DDInter, fichas técnicas): por cada par queda la de MAYOR severidad."""
from junta_medica.models.pharmacology.interaction import Interaction


def merge_interactions(*sources: list[Interaction]) -> list[Interaction]:
    """Ante la misma severidad se conserva la de la primera lista (por eso DDInter va primero)."""
    by_pair: dict[frozenset[str], Interaction] = {}
    for interactions in sources:
        for interaction in interactions:
            current = by_pair.get(interaction.pair)
            if current is None or interaction.severity.priority > current.severity.priority:
                by_pair[interaction.pair] = interaction
    return sorted(by_pair.values(), key=lambda i: (i.drug_a, i.drug_b))
