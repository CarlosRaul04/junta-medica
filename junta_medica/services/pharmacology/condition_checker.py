"""
ConditionChecker: revisa las reglas de cada medicamento del caso contra los datos del paciente.

Si varias reglas del MISMO medicamento y el MISMO dato se cumplen a la vez (ej. dabigatrán con TFG 28:
"< 30 contraindicado" y "< 50 reducir dosis"), solo se informa la más grave, para no repetir alertas.
"""
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.interfaces.condition_criterion import ConditionCriterion
from junta_medica.models.pharmacology.condition_finding import ConditionFinding, ConditionCheckResult
from junta_medica.models.pharmacology.condition_rule import ConditionRule, CriterionType
from junta_medica.models.pharmacology.severity import Severity


class ConditionChecker:
    def __init__(self, rules: list[ConditionRule], criteria: dict[CriterionType, ConditionCriterion],
                 reported_severities: list[str], highlighted_severities: list[str]):
        self._rules = rules
        self._criteria = criteria
        self._reported = {Severity(s) for s in reported_severities}
        self._highlighted = {Severity(s) for s in highlighted_severities}

    def detect(self, case: ClinicalCase, inns: list[str]) -> ConditionCheckResult:
        drugs = set(inns)
        findings, not_evaluable = [], []
        for rule in self._rules:
            if rule.drug not in drugs or rule.severity not in self._reported:
                continue
            evaluation = self._criteria[rule.criterion_type].evaluate(rule, case)
            if evaluation is None:
                not_evaluable.append(rule)
            elif evaluation[0]:
                findings.append(ConditionFinding(rule, evaluation[1], rule.severity in self._highlighted))
        return ConditionCheckResult(tuple(self._most_severe_per_parameter(findings)), tuple(not_evaluable))

    @staticmethod
    def _most_severe_per_parameter(findings: list[ConditionFinding]) -> list[ConditionFinding]:
        best: dict[tuple, ConditionFinding] = {}
        for finding in findings:                      # ante empate, queda la primera regla del archivo
            key = (finding.rule.drug, finding.rule.criterion_type, finding.rule.parameter)
            if key not in best or finding.rule.severity.priority > best[key].rule.severity.priority:
                best[key] = finding
        return sorted(best.values(), key=lambda h: -h.rule.severity.priority)
