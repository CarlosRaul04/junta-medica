"""ConditionRule: un medicamento es riesgoso por una característica del paciente (TFG, potasio, edad, antecedente)."""
from dataclasses import dataclass
from enum import Enum

from junta_medica.models.pharmacology.severity import Severity


class CriterionType(str, Enum):
    LAB = "lab"   # ej. egfr_ml_min < 30
    AGE = "age"                 # ej. edad > 60
    HISTORY = "history"   # ej. antecedente de insuficiencia cardiaca


@dataclass(frozen=True)
class ConditionRule:
    rule_id: str
    drug: str          # DCI
    criterion_type: CriterionType
    parameter: str            # clave de laboratorio, "edad" o nombre de la condición
    operator: str             # <, <=, >, >= (laboratorio/edad) · "contiene" (antecedente)
    value: str                # umbral numérico, o términos separados por | para antecedentes
    severity: Severity
    effect: str
    recommendation: str
    source: str               # id del catálogo de documentos (ej. gpc_dm2)
    page: int               # página del PDF

    @property
    def citation(self) -> str:
        return f"{self.source}:p{self.page}"
