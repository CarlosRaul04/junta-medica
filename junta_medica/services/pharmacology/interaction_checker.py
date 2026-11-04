"""
InteractionChecker: implementa el diagrama de flujo 3 del documento.

1. Se obtiene la lista de medicamentos (ya normalizados a DCI).
2. Para cada par, se busca en la tabla.
3. Si existe y su severidad se informa, se registra el hallazgo.
4. Si es grave, se marca como alerta destacada.
"""
from junta_medica.models.pharmacology.interaction_finding import InteractionFinding
from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity


class InteractionChecker:
    def __init__(self, interactions: list[Interaction], reported_severities: list[str],
                 highlighted_severities: list[str]):
        self._table = {i.pair: i for i in interactions}
        self._reported = {Severity(s) for s in reported_severities}
        self._highlighted = {Severity(s) for s in highlighted_severities}

    def detect(self, inns: list[str]) -> list[InteractionFinding]:
        drugs = list(dict.fromkeys(inns))  # sin repetidos, conservando el orden
        findings = []
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                interaction = self._table.get(frozenset((drugs[i], drugs[j])))
                if interaction and interaction.severity in self._reported:
                    findings.append(InteractionFinding(interaction, interaction.severity in self._highlighted))
        return sorted(findings, key=lambda h: -h.interaction.severity.priority)
