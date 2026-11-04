"""
AlertConsolidator: arma las alertas del informe.

- Las de la tabla de interacciones y las reglas fármaco–condición (calculadas sin IA) van SIEMPRE.
  La IA puede agregar alertas, pero nunca quitar una de estas (RF12, regla de diseño del PLAN).
- Las que agrega el Agente Farmacológico solo entran si tienen al menos una cita válida.
"""
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.final_alert import FinalAlert
from junta_medica.models.debate.review import Review
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.agents.context.observation_text import readable_observation


class AlertConsolidator:
    def __init__(self, severity_labels: dict[str, str], highlighted_severities: list[str], lab_labels: dict[str, str]):
        self._labels = severity_labels
        self._labs = lab_labels
        self._highlighted = {Severity(s) for s in highlighted_severities}

    def consolidate(self, evidence: CaseEvidence, pharmacological_reviews: list[Review],
                    allowed_citations: set[str]) -> list[FinalAlert]:
        alerts = [self._from_interaction(f) for f in evidence.interactions]
        alerts += [self._from_condition(f) for f in evidence.conditions.findings]
        alerts += self._from_agent(pharmacological_reviews, allowed_citations, {a.text for a in alerts})
        return sorted(alerts, key=lambda a: -a.severity.priority)

    def _from_interaction(self, finding) -> FinalAlert:
        i = finding.interaction
        return FinalAlert(f"Interacción {self._labels[i.severity.value]}: {i.drug_a} + {i.drug_b}.",
                          i.severity, (i.citation,), "interaction_table", finding.highlighted)

    def _from_condition(self, finding) -> FinalAlert:
        rule = finding.rule
        return FinalAlert(f"{rule.drug} ({readable_observation(finding.observed_value, self._labs)}): {rule.effect} {rule.recommendation}",
                          rule.severity, (rule.citation,), "condition_rules", finding.highlighted)

    def _from_agent(self, reviews: list[Review], allowed: set[str], existing: set[str]) -> list[FinalAlert]:
        alerts = []
        for review in reviews:
            for item in review.additional_alerts:
                citations = tuple(c for c in item.citations if c in allowed)
                if citations and item.text not in existing:
                    existing.add(item.text)
                    alerts.append(FinalAlert(item.text, Severity.MODERATE, citations, "agent", False))
        return alerts
