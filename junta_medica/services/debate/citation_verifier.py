"""
CitationVerifier: revisa que cada cita de los agentes esté entre las que el sistema les entregó.

Una cita fuera de esa lista es inventada (o mal escrita): se informa como inválida.
La trazabilidad es la proporción de afirmaciones con al menos una cita válida (meta del documento: >= 90 %).
Se cuentan: diagnósticos y plan de la ÚLTIMA propuesta, objeciones y alertas de la última ronda,
y recomendaciones del Médico Jefe.
"""
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.chief_verdict import ChiefVerdict
from junta_medica.models.debate.citation_check import CitationCheck
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.review import Review


class CitationVerifier:
    def check(self, final_turns: list[AgentTurn], allowed: set[str]) -> CitationCheck:
        valid, invalid = [], []
        cited, total = 0, 0
        for turn in final_turns:
            for citations in self._claims(turn.output):
                total += 1
                good = [c for c in citations if c in allowed]
                valid += good
                invalid += [c for c in citations if c not in allowed]
                cited += 1 if good else 0
        return CitationCheck(tuple(dict.fromkeys(valid)), tuple(dict.fromkeys(invalid)), cited, total)

    @staticmethod
    def _claims(output) -> list[tuple[str, ...]]:
        if isinstance(output, ClinicalProposal):
            return [d.citations for d in output.diagnoses] + [p.citations for p in output.plan]
        if isinstance(output, Review):
            return [o.citations for o in output.objections] + [a.citations for a in output.additional_alerts]
        if isinstance(output, ChiefVerdict):
            return [r.citations for r in output.recommendations]
        return []
