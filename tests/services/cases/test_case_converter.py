from junta_medica.services.cases.case_converter import CaseConverter
from junta_medica.models.cases.clinical_case import Medication, Sex


def test_converts_and_cleans_data(valid_case):
    valid_case["sex"] = " m "
    valid_case["symptoms"] = [" cefalea ", "", "mareos"]
    case = CaseConverter().convert(valid_case)
    assert case.sex is Sex.MALE
    assert case.symptoms == ("cefalea", "mareos")


def test_accepts_medications_as_text_or_with_dose(valid_case):
    case = CaseConverter().convert(valid_case)
    assert case.medications == (Medication("enalapril", "10 mg cada 12 h"), Medication("metformina"))
    assert case.medication_names == ["enalapril", "metformina"]


def test_missing_optional_fields_are_empty(valid_case):
    for field in ("medical_history", "allergies", "lab_results"):
        del valid_case[field]
    case = CaseConverter().convert(valid_case)
    assert case.medical_history == () and case.allergies == () and case.lab_results == {}
