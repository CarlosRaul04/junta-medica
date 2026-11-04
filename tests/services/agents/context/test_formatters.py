from junta_medica.config import cases as cases_config
from junta_medica.config import texts
from junta_medica.factories.case_factory import create_case_loader
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.cited_item import CitedItem
from junta_medica.models.debate.objection import Objection
from junta_medica.models.debate.proposed_diagnosis import ProposedDiagnosis
from junta_medica.models.debate.review import Review
from junta_medica.models.debate.stance import Stance
from junta_medica.models.pharmacology.normalized_drug import NormalizationMethod, NormalizedDrug
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.context.evidence_formatter import EvidenceFormatter


def test_case_formatter_uses_readable_lab_names(valid_case):
    text = CaseFormatter(cases_config.RECOGNIZED_LAB_TESTS).full(create_case_loader().from_dict(valid_case))
    assert "TFG estimada (mL/min/1.73 m²): 55" in text
    assert "enalapril (10 mg cada 12 h)" in text
    assert "expected" not in text


def test_pharmacological_profile_omits_symptoms(valid_case):
    text = CaseFormatter(cases_config.RECOGNIZED_LAB_TESTS).clinical_profile(create_case_loader().from_dict(valid_case))
    assert "cefalea" not in text and "penicilina" in text


def test_drug_list_marks_unrecognized_and_brand_names():
    drugs = (NormalizedDrug("Pradaxa", "dabigatrán", NormalizationMethod.BRAND),
             NormalizedDrug("fluconazol", None, NormalizationMethod.UNRECOGNIZED))
    text = EvidenceFormatter(texts.SEVERITY_LABELS, 100, {}).drugs(drugs)
    assert "Pradaxa -> dabigatrán" in text and "fluconazol: NO RECONOCIDO" in text


def test_debate_formatter_shows_stance_objections_and_citations():
    review = Review(Stance.OBJECTION, (Objection(Severity.SEVERE, "Mantiene AINE", ("ddinter:1",)),))
    text = DebateFormatter(texts.STANCE_LABELS, texts.ROLE_LABELS, texts.SEVERITY_LABELS).review("pharmacological", review)
    assert "Agente Farmacológico — postura: objeción" in text
    assert "Objeción grave: Mantiene AINE [ddinter:1]" in text


def test_proposal_text():
    proposal = ClinicalProposal((ProposedDiagnosis("I10", "HTA", "high", "PA alta", ("gpc_hta:p15",)),),
                                (CitedItem("Iniciar IECA", ("gpc_hta:p16",)),))
    text = DebateFormatter(texts.STANCE_LABELS, texts.ROLE_LABELS, texts.SEVERITY_LABELS).proposal(proposal)
    assert "I10 HTA (probabilidad high): PA alta [gpc_hta:p15]" in text and "Iniciar IECA [gpc_hta:p16]" in text
