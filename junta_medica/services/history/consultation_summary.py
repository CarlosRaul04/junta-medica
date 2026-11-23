"""consultation_summary(): arma el resumen que va al historial a partir del resultado (ResultReader)."""
from junta_medica.models.history.new_consultation import NewConsultation
from junta_medica.services.reports.result_reader import ResultReader


def consultation_summary(result: ResultReader, user_id: int, result_key: str,
                         insufficient_label: str) -> NewConsultation:
    primary = result.primary_diagnosis or {}
    return NewConsultation(
        case_id=result.case_id,
        user_id=user_id,
        insufficient_evidence=result.insufficient_evidence,
        primary_icd10=primary.get("icd10", "") if not result.abstained else "",
        primary_name=insufficient_label if result.abstained else primary.get("name", ""),
        agreement=result.agreement,
        rounds=len(result.rounds),
        severe_alerts=len(result.highlighted_alerts),
        traceability=result.traceability,
        seconds=result.seconds,
        llm_calls=result.llm_calls,
        models=", ".join(result.models),
        result_key=result_key,
    )
