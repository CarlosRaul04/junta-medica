"""CaseConverter: convierte un diccionario YA VALIDADO en un ClinicalCase (limpia espacios y textos vacíos)."""
from junta_medica.models.cases.clinical_case import ClinicalCase, Medication, Sex


class CaseConverter:
    def convert(self, data: dict) -> ClinicalCase:
        return ClinicalCase(
            case_id=data["case_id"].strip(),
            age=data["age"],
            sex=Sex(data["sex"].strip().upper()),
            chief_complaint=data["chief_complaint"].strip(),
            symptoms=self._clean_texts(data["symptoms"]),
            medications=tuple(self._parse_medication(m) for m in data["medications"]),
            medical_history=self._clean_texts(data.get("medical_history", [])),
            allergies=self._clean_texts(data.get("allergies", [])),
            lab_results=dict(data.get("lab_results", {})),
        )

    @staticmethod
    def _clean_texts(texts: list[str]) -> tuple[str, ...]:
        return tuple(text.strip() for text in texts if text.strip())

    @staticmethod
    def _parse_medication(drug: str | dict) -> Medication:
        """Acepta "warfarina" o {"nombre": "warfarina", "dosis": "5 mg/día"}."""
        if isinstance(drug, str):
            return Medication(name=drug.strip())
        return Medication(name=drug["name"].strip(), dose=drug.get("dose", "").strip())
