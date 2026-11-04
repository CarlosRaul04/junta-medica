"""QueryBuilder: arma las consultas al buscador de guías (a partir del caso, o de la propuesta del Clínico)."""
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.debate.clinical_proposal import ClinicalProposal


class QueryBuilder:
    def __init__(self, max_chars: int):
        self._max = max_chars

    def for_case(self, case: ClinicalCase) -> list[str]:
        """
        Tres miradas del caso: lo que le pasa (motivo + síntomas), su contexto (motivo + antecedentes)
        y su tratamiento actual (antecedentes + medicación: trae las recomendaciones de uso de esos fármacos,
        ej. espironolactona y potasio en la guía de IC).
        """
        queries = [self._join([case.chief_complaint, *case.symptoms])]
        if case.medical_history:
            queries.append(self._join([case.chief_complaint, *case.medical_history]))
        queries.append(self._join([*case.medical_history, "tratamiento con " + ", ".join(case.medication_names)]))
        return queries

    def for_proposal(self, proposal: ClinicalProposal) -> list[str]:
        """Una consulta por diagnóstico (su manejo) y otra con el plan completo."""
        queries = [self._join([f"tratamiento de {d.name}"]) for d in proposal.diagnoses if d.name]
        if proposal.plan:
            queries.append(self._join([item.text for item in proposal.plan]))
        return queries

    def _join(self, parts: list[str]) -> str:
        text = ". ".join(p.strip() for p in parts if p and p.strip())
        return text[: self._max].rsplit(" ", 1)[0] if len(text) > self._max else text
