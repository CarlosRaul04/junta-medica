"""ConditionRuleRepository: lee las reglas fármaco–condición (data/pharmacology/condition_rules.csv)."""
import csv
from pathlib import Path

from junta_medica.models.pharmacology.condition_rule import ConditionRule, CriterionType
from junta_medica.models.pharmacology.severity import Severity


class ConditionRuleRepository:
    def __init__(self, path: Path):
        self._path = path

    def read_all(self) -> list[ConditionRule]:
        with open(self._path, encoding="utf-8", newline="") as file:
            return [
                ConditionRule(
                    rule_id=f["rule_id"].strip(),
                    drug=f["drug"].strip(),
                    criterion_type=CriterionType(f["criterion_type"].strip()),
                    parameter=f["parameter"].strip(),
                    operator=f["operator"].strip(),
                    value=f["value"].strip(),
                    severity=Severity(f["severity"].strip()),
                    effect=f["effect"].strip(),
                    recommendation=f["recommendation"].strip(),
                    source=f["source"].strip(),
                    page=int(f["page"]),
                )
                for f in csv.DictReader(file)
            ]
