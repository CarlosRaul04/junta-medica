"""DebateFormatter: propuestas y revisiones como texto (para que un agente lea lo que dijeron los otros)."""
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.debate_round import DebateRound
from junta_medica.models.debate.review import Review


class DebateFormatter:
    def __init__(self, stance_labels: dict[str, str], role_labels: dict[str, str], severity_labels: dict[str, str]):
        self._stance = stance_labels
        self._role = role_labels
        self._severity = severity_labels

    def proposal(self, proposal: ClinicalProposal) -> str:
        lines = ["Diagnósticos propuestos:"]
        for d in proposal.diagnoses:
            lines.append(f"- {d.icd10} {d.name} (probabilidad {d.likelihood}): {d.rationale} {self._cites(d.citations)}")
        lines.append("Plan:")
        lines += [f"- {item.text} {self._cites(item.citations)}" for item in proposal.plan] or ["- (sin plan)"]
        if proposal.missing_data:
            lines.append("Datos que faltan: " + "; ".join(proposal.missing_data))
        if proposal.response_to_objections:
            lines.append("Respuesta a las objeciones: " + " ".join(proposal.response_to_objections))
        return "\n".join(lines)

    def review(self, role: str, review: Review) -> str:
        lines = [f"{self._role.get(role, role)} — postura: {self._stance[review.stance.value]}"]
        for o in review.objections:
            lines.append(f"- Objeción {self._severity[o.severity.value]}: {o.detail} {self._cites(o.citations)}")
        lines += [f"- Comentario: {c}" for c in review.comments]
        lines += [f"- Alerta adicional: {a.text} {self._cites(a.citations)}" for a in review.additional_alerts]
        return "\n".join(lines)

    def feedback(self, reviews: list[tuple[str, Review]]) -> str:
        """Lo que el Agente Clínico debe responder en la ronda siguiente."""
        return "\n\n".join(self.review(role, review) for role, review in reviews)

    def rounds(self, rounds: tuple[DebateRound, ...] | list[DebateRound]) -> str:
        blocks = []
        for r in rounds:
            reviews = "\n".join(self.review(t.role, t.output) for t in r.reviews)
            blocks.append(f"### Ronda {r.number} (acuerdo {r.agreement_level:.0%})\n{self.proposal(r.proposal.output)}\n{reviews}")
        return "\n\n".join(blocks)

    @staticmethod
    def _cites(citations) -> str:
        return " ".join(f"[{c}]" for c in citations)
