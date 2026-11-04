from junta_medica.config import debate as config
from junta_medica.models.debate.stance import Stance
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.agents.parsing.chief_verdict_parser import ChiefVerdictParser
from junta_medica.services.agents.parsing.clinical_proposal_parser import ClinicalProposalParser
from junta_medica.services.agents.parsing.field_readers import read_citations
from junta_medica.services.agents.parsing.review_parser import ReviewParser

clinical = ClinicalProposalParser(config.MAX_DIAGNOSES, config.VALID_LIKELIHOODS, config.LIKELIHOOD_SYNONYMS,
                                  config.DEFAULT_LIKELIHOOD)
reviews = ReviewParser(config.STANCE_SYNONYMS, config.UNKNOWN_STANCE)


def test_citations_in_any_format():
    assert read_citations("[gpc_ic:p23], ft_x:p5") == ("gpc_ic:p23", "ft_x:p5")
    assert read_citations(["gpc_ic:p23", "gpc_ic:p23"]) == ("gpc_ic:p23",)
    assert read_citations(None) == ()


def test_clinical_proposal_keeps_top_3_and_normalizes_fields():
    data = {"diagnoses": [{"icd10": "i50.0 ", "name": "IC", "likelihood": "alta", "citations": "gpc_ic:p16"}] * 4,
            "plan": ["Reducir sal", {"text": "iSGLT2", "citations": ["gpc_ic:p24"]}]}
    proposal = clinical.parse(data)
    assert len(proposal.diagnoses) == 3
    d = proposal.diagnoses[0]
    assert (d.icd10, d.likelihood, d.citations) == ("I50.0", "high", ("gpc_ic:p16",))
    assert [p.text for p in proposal.plan] == ["Reducir sal", "iSGLT2"]
    assert proposal.missing_data == ()


def test_empty_response_gives_empty_proposal():
    proposal = clinical.parse({})
    assert proposal.diagnoses == () and proposal.plan == ()


def test_stance_in_spanish_and_unknown_stance_is_objection():
    assert reviews.parse({"stance": "De acuerdo"}).stance is Stance.AGREE
    assert reviews.parse({"stance": "objeción"}).stance is Stance.OBJECTION
    assert reviews.parse({"stance": "quizás"}).stance is Stance.OBJECTION
    assert reviews.parse({}).stance is Stance.OBJECTION


def test_agree_with_objections_is_not_lost():
    review = reviews.parse({"stance": "agree", "objections": [{"severity": "grave", "detail": "Riesgo"}]})
    assert review.stance is Stance.AGREE_WITH_COMMENTS
    assert review.objections[0].severity is Severity.SEVERE


def test_objection_written_as_plain_text():
    review = reviews.parse({"stance": "objection", "objections": "Falta anticoagular"})
    assert review.objections[0].detail == "Falta anticoagular"
    assert review.objections[0].severity is Severity.MODERATE


def test_chief_verdict():
    verdict = ChiefVerdictParser(config.MAX_DIFFERENTIALS).parse({
        "summary": "Texto", "primary_diagnosis": {"icd10": "e87.5", "name": "Hiperpotasemia"},
        "differential_diagnoses": [{"icd10": "I50.0", "name": "IC"}, {"icd10": "N18", "name": "ERC"}, {"name": "x"}],
        "recommendations": [{"text": "Suspender", "citations": ["gpc_ic:p23"]}], "insufficient_evidence": "false"})
    assert verdict.primary_diagnosis.icd10 == "E87.5"
    assert len(verdict.differential_diagnoses) == 2
    assert verdict.insufficient_evidence is False
    assert ChiefVerdictParser(2).parse({}).primary_diagnosis is None


def test_stray_closing_brace_at_the_end_is_removed():
    from junta_medica.services.agents.parsing.field_readers import read_text
    assert read_text("... y frecuencia cardíaca.}") == "... y frecuencia cardíaca."
    assert read_text("Dosis {ajustada}") == "Dosis {ajustada}"


def test_citation_written_inside_the_text_is_moved_to_citations():
    review = reviews.parse({"stance": "agree", "additional_alerts": [
        {"text": "Enalapril puede mantener elevada la potasemia. [gpc_ic:p23-24]", "citations": []}],
        "objections": ["Falta ECG [ddinter:DDInter1-DDInter2]"]})
    alert = review.additional_alerts[0]
    assert alert.text == "Enalapril puede mantener elevada la potasemia."
    assert alert.citations == ("gpc_ic:p23-24",)
    assert review.objections[0].citations == ("ddinter:DDInter1-DDInter2",)
