"""CaseFormatter: el caso clínico como texto para el mensaje de un agente (nunca incluye la sección "expected")."""
from junta_medica.models.cases.clinical_case import ClinicalCase

NONE = "ninguno registrado"


class CaseFormatter:
    def __init__(self, lab_labels: dict[str, str]):
        self._lab_labels = lab_labels

    def full(self, case: ClinicalCase) -> str:
        return "\n".join([
            self._header(case),
            f"Síntomas: {self._join(case.symptoms)}",
            f"Antecedentes: {self._join(case.medical_history)}",
            f"Alergias: {self._join(case.allergies)}",
            f"Medicación actual: {self._join(self._medications(case))}",
            f"Laboratorio y signos: {self._labs(case)}",
        ])

    def summary(self, case: ClinicalCase) -> str:
        return "\n".join([self._header(case), f"Antecedentes: {self._join(case.medical_history)}"])

    def clinical_profile(self, case: ClinicalCase) -> str:
        """Lo que necesita el Agente Farmacológico: sin el relato de síntomas."""
        return "\n".join([
            f"Paciente: {case.age} años, sexo {case.sex.value}.",
            f"Antecedentes: {self._join(case.medical_history)}",
            f"Alergias: {self._join(case.allergies)}",
            f"Laboratorio y signos: {self._labs(case)}",
        ])

    @staticmethod
    def _header(case: ClinicalCase) -> str:
        return f"Caso {case.case_id}: {case.age} años, sexo {case.sex.value}.\nMotivo de consulta: {case.chief_complaint}"

    @staticmethod
    def _medications(case: ClinicalCase) -> list[str]:
        return [f"{m.name} ({m.dose})" if m.dose else m.name for m in case.medications]

    def _labs(self, case: ClinicalCase) -> str:
        if not case.lab_results:
            return NONE
        return "; ".join(f"{self._lab_labels.get(k, k)}: {v:g}" for k, v in case.lab_results.items())

    @staticmethod
    def _join(items) -> str:
        return "; ".join(items) if items else NONE
