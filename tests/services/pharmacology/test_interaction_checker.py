import pytest

from junta_medica.factories.pharmacology_factory import create_interaction_checker
from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.pharmacology.interaction_checker import InteractionChecker

TABLE = [
    Interaction("ibuprofeno", "warfarina", Severity.SEVERE, "DDInter", "D1-D2"),
    Interaction("metformina", "insulina", Severity.MODERATE, "DDInter", "D3-D4"),
    Interaction("omeprazol", "warfarina", Severity.MILD, "DDInter", "D5-D1"),
]


@pytest.fixture
def checker():
    return InteractionChecker(TABLE, ["severe", "moderate"], ["severe"])


def test_cp02_severe_interaction_is_highlighted(checker):
    findings = checker.detect(["warfarina", "enalapril", "ibuprofeno"])
    assert len(findings) == 1 and findings[0].highlighted


def test_cp03_no_pairs_in_table_means_no_alerts(checker):
    assert checker.detect(["enalapril", "amlodipino"]) == []


def test_moderate_is_reported_not_highlighted_and_mild_is_not_reported(checker):
    findings = checker.detect(["metformina", "insulina", "omeprazol", "warfarina"])
    assert [(h.interaction.severity, h.highlighted) for h in findings] == [(Severity.MODERATE, False)]


def test_sorts_by_severity_and_ignores_duplicates(checker):
    findings = checker.detect(["insulina", "metformina", "warfarina", "ibuprofeno", "warfarina"])
    assert [h.interaction.severity for h in findings] == [Severity.SEVERE, Severity.MODERATE]


@pytest.mark.parametrize("pair", [
    ("warfarina", "ibuprofeno"), ("amiodarona", "digoxina"), ("enalapril", "espironolactona"),
    ("enalapril", "losartán"), ("atorvastatina", "claritromicina"), ("amiodarona", "levofloxacino"),
])
def test_real_table_detects_known_severe_interactions(pair):
    findings = create_interaction_checker().detect(list(pair))
    assert findings and findings[0].highlighted
