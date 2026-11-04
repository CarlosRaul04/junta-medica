from junta_medica.models.cases.clinical_case import ClinicalCase, Medication, Sex
from junta_medica.factories.pharmacology_factory import create_condition_checker


def case(age=70, medical_history=(), lab_results=None, drugs=()):
    return ClinicalCase("CASO-001", age, Sex.MALE, "m", ("s",),
                       tuple(Medication(m) for m in drugs), medical_history, (), lab_results or {})


def detect(**kwargs):
    c = case(**kwargs)
    return create_condition_checker().detect(c, c.medication_names)


def test_metformin_with_low_egfr_is_severe_alert_citing_the_guideline():
    result = detect(drugs=["metformina"], lab_results={"egfr_ml_min": 25})
    assert [h.rule.rule_id for h in result.findings] == ["RC01"]
    assert result.findings[0].highlighted
    assert result.findings[0].rule.citation == "gpc_dm2:p31"


def test_metformin_with_normal_egfr_has_no_finding():
    assert detect(drugs=["metformina"], lab_results={"egfr_ml_min": 75}).findings == ()


def test_rule_without_data_is_not_evaluable():
    result = detect(drugs=["metformina"])
    assert result.findings == () and [r.rule_id for r in result.not_evaluable] == ["RC01"]


def test_spironolactone_with_hyperkalemia_and_low_egfr_keeps_the_most_severe_per_lab():
    result = detect(drugs=["espironolactona"], lab_results={"egfr_ml_min": 25, "potassium_meq_l": 6.3})
    ids = {h.rule.rule_id for h in result.findings}
    assert ids == {"RC08", "RC09"}   # RC10 (K >= 5, moderada) queda cubierta por RC09 (K > 6, grave)


def test_findings_sorted_by_severity():
    result = detect(drugs=["espironolactona"], lab_results={"egfr_ml_min": 60, "potassium_meq_l": 5.2,
                                                               "creatinine_mg_dl": 2.6})
    assert [h.rule.severity.value for h in result.findings] == ["moderate", "moderate"]
    result = detect(drugs=["espironolactona", "metformina"], lab_results={"egfr_ml_min": 25, "potassium_meq_l": 5.2})
    severities = [h.rule.severity.priority for h in result.findings]
    assert severities == sorted(severities, reverse=True)


def test_history_and_age_rules():
    result = detect(age=72, drugs=["pioglitazona", "glibenclamida"],
                         medical_history=("Insuficiencia cardiaca crónica",), lab_results={"egfr_ml_min": 60})
    assert {h.rule.rule_id for h in result.findings} == {"RC04", "RC05"}


def test_only_case_drugs_are_checked():
    assert detect(drugs=["enalapril"], lab_results={"egfr_ml_min": 10}).findings == ()


def test_reports_only_the_most_severe_rule_per_drug_and_parameter(valid_case):
    from junta_medica.factories.case_factory import create_case_loader
    from junta_medica.factories.pharmacology_factory import create_condition_checker
    valid_case["medications"] = ["dabigatrán"]
    valid_case["lab_results"] = {"egfr_ml_min": 28}
    result = create_condition_checker().detect(create_case_loader().from_dict(valid_case), ["dabigatrán"])
    renal = [f.rule.rule_id for f in result.findings if f.rule.parameter == "egfr_ml_min"]
    assert len(renal) == 1
    assert result.findings[0].rule.severity.value == "severe"
