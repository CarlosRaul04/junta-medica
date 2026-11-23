"""Consultation: una consulta registrada en el historial (RF16): el resumen para listar, filtrar y exportar."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Consultation:
    consultation_id: int
    case_id: str
    created_at: str                 # ISO 8601, UTC
    user_id: int
    username: str
    insufficient_evidence: bool     # RF11
    primary_icd10: str
    primary_name: str
    agreement: float                # nivel de acuerdo final (0 a 1)
    rounds: int
    severe_alerts: int
    traceability: float             # 0 a 1
    seconds: float
    llm_calls: int
    models: str                     # modelos usados, separados por coma
    result_key: str                 # dónde quedó el JSON completo (FileStorage)
    report_key: str = ""            # dónde quedó el informe PDF (FileStorage)
