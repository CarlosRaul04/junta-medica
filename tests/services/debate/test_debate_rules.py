"""Reglas deterministas del debate: consenso, citas, alertas y consultas."""
from junta_medica.config import texts
from junta_medica.factories.case_factory import create_case_loader
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.chief_verdict import ChiefVerdict
from junta_medica.models.debate.cited_item import CitedItem
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.proposed_diagnosis import ProposedDiagnosis
from junta_medica.models.debate.review import Review
from junta_medica.models.debate.stance import Stance
from junta_medica.models.llm.llm_response import LLMResponse
from junta_medica.services.debate.alert_consolidator import AlertConsolidator
from junta_medica.services.debate.citation_verifier import CitationVerifier
from junta_medica.services.debate.consensus_calculator import ConsensusCalculator
from junta_medica.services.debate.query_builder import QueryBuilder

LLM = LLMResponse("x", "m", {}, 0, 0, 0.0, 0.0, 1, True)


def test_consensus_two_thirds_passes_threshold():
    calculator = ConsensusCalculator(0.67)
    assert calculator.evaluate([Review(Stance.AGREE), Review(Stance.AGREE_WITH_COMMENTS)]) == (1.0, True)
    assert calculator.evaluate([Review(Stance.AGREE), Review(Stance.OBJECTION)]) == (0.67, True)
    assert calculator.evaluate([Review(Stance.OBJECTION), Review(Stance.OBJECTION)]) == (0.33, False)


def test_a_severe_objection_blocks_consensus_even_above_threshold():
    from junta_medica.models.debate.objection import Objection
    from junta_medica.models.pharmacology.severity import Severity
    severe = Review(Stance.OBJECTION, (Objection(Severity.SEVERE, "Riesgo de sangrado"),))
    moderate = Review(Stance.OBJECTION, (Objection(Severity.MODERATE, "Falta un control"),))
    assert ConsensusCalculator(0.67).evaluate([Review(Stance.AGREE), severe]) == (0.67, False)
    assert ConsensusCalculator(0.67).evaluate([Review(Stance.AGREE), moderate]) == (0.67, True)


def test_citation_verifier_detects_invented_citations_and_measures_traceability():
    proposal = ClinicalProposal((ProposedDiagnosis("I10", "HTA", "high", "", ("gpc_hta:p15",)),),
                                (CitedItem("Dieta", ()), CitedItem("IECA", ("gpc_hta:p99",))))
    verdict = ChiefVerdict("x", None, recommendations=(CitedItem("Control", ("gpc_hta:p15", "inventada:p1")),))
    check = CitationVerifier().check([AgentTurn("clinical", 1, proposal, LLM), AgentTurn("chief", 0, verdict, LLM)],
                                     {"gpc_hta:p15"})
    assert check.invalid == ("gpc_hta:p99", "inventada:p1")
    assert (check.cited_claims, check.total_claims) == (2, 4)
    assert check.traceability == 0.5


def test_table_alerts_always_included_and_agent_alerts_need_valid_citation(valid_case):
    from junta_medica.factories.debate_factory import create_debate_orchestrator  # noqa: F401  (solo verifica imports)
    from junta_medica.factories.pharmacology_factory import create_condition_checker, create_interaction_checker
    from junta_medica.models.debate.case_evidence import CaseEvidence
    from junta_medica.models.knowledge.search_result import SearchResult
    valid_case["medications"] = ["warfarina", "ibuprofeno", "metformina"]
    valid_case["lab_results"] = {"egfr_ml_min": 25}
    case = create_case_loader().from_dict(valid_case)
    inns = ["warfarina", "ibuprofeno", "metformina"]
    evidence = CaseEvidence(case, (), tuple(create_interaction_checker().detect(inns)),
                            create_condition_checker().detect(case, inns), SearchResult("q", (), True))
    agent_review = Review(Stance.AGREE, additional_alerts=(CitedItem("Con cita", ("gpc_dm2:p31",)),
                                                           CitedItem("Sin cita válida", ("inventada",))))
    alerts = AlertConsolidator(texts.SEVERITY_LABELS, ["severe"], {"egfr_ml_min": "TFG estimada"}).consolidate(evidence, [agent_review], {"gpc_dm2:p31"})
    origins = [a.origin for a in alerts]
    assert "interaction_table" in origins and "condition_rules" in origins
    assert [a.text for a in alerts if a.origin == "agent"] == ["Con cita"]
    assert alerts[0].highlighted                       # ordenadas: la grave primero
    assert any("metformina (TFG estimada = 25)" in a.text for a in alerts)


def test_queries_from_case_and_proposal(valid_case):
    builder = QueryBuilder(60)
    queries = builder.for_case(create_case_loader().from_dict(valid_case))
    assert len(queries) == 3 and all(len(q) <= 60 for q in queries)
    assert "enalapril" in QueryBuilder(400).for_case(create_case_loader().from_dict(valid_case))[-1]
    proposal = ClinicalProposal((ProposedDiagnosis("I10", "hipertensión", "high", ""),), (CitedItem("dieta"),))
    assert builder.for_proposal(proposal) == ["tratamiento de hipertensión", "dieta"]
