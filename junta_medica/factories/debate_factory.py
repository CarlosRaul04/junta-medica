"""
Arma el DebateOrchestrator con sus agentes, herramientas y parámetros (config/debate.py, config/texts.py).

Se le puede pasar un buscador o un cliente de IA ya armados (las pruebas usan versiones falsas).
"""
from junta_medica.config import cases as cases_config
from junta_medica.config import debate as config
from junta_medica.config import knowledge as knowledge_config
from junta_medica.config import paths, texts
from junta_medica.config import pharmacology as pharmacology_config
from junta_medica.factories.knowledge_factory import create_retriever
from junta_medica.factories.llm_factory import create_llm_client
from junta_medica.factories.pharmacology_factory import (
    create_condition_checker, create_drug_normalizer, create_interaction_checker,
)
from junta_medica.repositories.debate.debate_result_repository import DebateResultRepository
from junta_medica.repositories.prompts.prompt_repository import PromptRepository
from junta_medica.services.agents.chief_agent import ChiefAgent
from junta_medica.services.agents.clinical_agent import ClinicalAgent
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.context.evidence_formatter import EvidenceFormatter
from junta_medica.services.agents.parsing.chief_verdict_parser import ChiefVerdictParser
from junta_medica.services.agents.parsing.clinical_proposal_parser import ClinicalProposalParser
from junta_medica.services.agents.parsing.review_parser import ReviewParser
from junta_medica.services.agents.pharmacological_agent import PharmacologicalAgent
from junta_medica.services.agents.protocol_agent import ProtocolAgent
from junta_medica.services.debate.abstention_policy import AbstentionPolicy
from junta_medica.services.debate.alert_consolidator import AlertConsolidator
from junta_medica.services.debate.citation_verifier import CitationVerifier
from junta_medica.services.debate.consensus_calculator import ConsensusCalculator
from junta_medica.services.debate.debate_orchestrator import DebateOrchestrator
from junta_medica.services.debate.evidence_collector import EvidenceCollector
from junta_medica.services.debate.query_builder import QueryBuilder
from junta_medica.services.knowledge.retriever import KnowledgeRetriever
from junta_medica.services.llm.llm_client import LLMClient


def create_debate_orchestrator(retriever: KnowledgeRetriever | None = None,
                               llm_client: LLMClient | None = None) -> DebateOrchestrator:
    retriever = retriever or create_retriever()
    client = llm_client or create_llm_client()
    prompts = PromptRepository(paths.PROMPTS_DIR)
    queries = QueryBuilder(config.QUERY_MAX_CHARS)

    cases = CaseFormatter(cases_config.RECOGNIZED_LAB_TESTS)
    evidence = EvidenceFormatter(texts.SEVERITY_LABELS, config.FRAGMENT_MAX_CHARS, cases_config.RECOGNIZED_LAB_TESTS)
    debate = DebateFormatter(texts.STANCE_LABELS, texts.ROLE_LABELS, texts.SEVERITY_LABELS)
    review_parser = ReviewParser(config.STANCE_SYNONYMS, config.UNKNOWN_STANCE)
    clinical_parser = ClinicalProposalParser(config.MAX_DIAGNOSES, config.VALID_LIKELIHOODS,
                                             config.LIKELIHOOD_SYNONYMS, config.DEFAULT_LIKELIHOOD)

    return DebateOrchestrator(
        collector=EvidenceCollector(create_drug_normalizer(), create_interaction_checker(),
                                    create_condition_checker(), retriever, queries, config.CLINICAL_FRAGMENTS),
        retriever=retriever,
        queries=queries,
        clinical=ClinicalAgent(client, prompts, clinical_parser, cases, evidence, debate),
        pharmacological=PharmacologicalAgent(client, prompts, review_parser, cases, evidence, debate),
        protocol=ProtocolAgent(client, prompts, review_parser, cases, evidence, debate),
        chief=ChiefAgent(client, prompts, ChiefVerdictParser(config.MAX_DIFFERENTIALS), cases, debate,
                         texts.SEVERITY_LABELS),
        consensus=ConsensusCalculator(config.CONSENSUS_THRESHOLD),
        abstention=AbstentionPolicy(config.ABSTAIN_WITHOUT_DEBATE),
        alerts=AlertConsolidator(texts.SEVERITY_LABELS, pharmacology_config.HIGHLIGHTED_SEVERITIES,
                                cases_config.RECOGNIZED_LAB_TESTS),
        citations=CitationVerifier(),
        max_rounds=config.MAX_ROUNDS,
        protocol_fragments=config.PROTOCOL_FRAGMENTS,
        abstention_message=texts.ABSTENTION_MESSAGE,
    )


def create_debate_result_repository() -> DebateResultRepository:
    return DebateResultRepository(paths.DEBATES_DIR, knowledge_config.EMBEDDING_MODEL)
