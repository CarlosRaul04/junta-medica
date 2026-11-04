from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.pharmacology.interaction_merger import merge_interactions


def interaction(a, b, severity, source):
    return Interaction(a, b, Severity(severity), source, "1")


def test_keeps_highest_severity_of_the_pair():
    ddinter = [interaction("a", "b", "moderate", "DDInter")]
    labels = [interaction("a", "b", "severe", "ft_x")]
    merged = merge_interactions(ddinter, labels)
    assert len(merged) == 1 and merged[0].severity is Severity.SEVERE and merged[0].source == "ft_x"


def test_on_tie_keeps_the_first_source():
    merged = merge_interactions([interaction("a", "b", "severe", "DDInter")], [interaction("a", "b", "severe", "ft_x")])
    assert merged[0].source == "DDInter"


def test_adds_pairs_missing_in_the_first_source():
    merged = merge_interactions([interaction("a", "b", "mild", "DDInter")], [interaction("c", "d", "moderate", "ft_x")])
    assert [(i.drug_a, i.drug_b) for i in merged] == [("a", "b"), ("c", "d")]
