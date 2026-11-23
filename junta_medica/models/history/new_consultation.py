"""NewConsultation: los datos de una consulta antes de guardarla (todavía sin id ni fecha)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class NewConsultation:
    case_id: str
    user_id: int
    insufficient_evidence: bool
    primary_icd10: str
    primary_name: str
    agreement: float
    rounds: int
    severe_alerts: int
    traceability: float
    seconds: float
    llm_calls: int
    models: str
    result_key: str
    report_key: str = ""
