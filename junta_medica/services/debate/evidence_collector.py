"""EvidenceCollector: corre todas las herramientas SIN IA sobre un caso. Es la base que reciben los agentes."""
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.services.debate.query_builder import QueryBuilder
from junta_medica.services.knowledge.retriever import KnowledgeRetriever
from junta_medica.services.pharmacology.condition_checker import ConditionChecker
from junta_medica.services.pharmacology.drug_normalizer import DrugNormalizer
from junta_medica.services.pharmacology.interaction_checker import InteractionChecker


class EvidenceCollector:
    def __init__(self, normalizer: DrugNormalizer, interactions: InteractionChecker, conditions: ConditionChecker,
                 retriever: KnowledgeRetriever, queries: QueryBuilder, fragments_limit: int):
        self._normalizer = normalizer
        self._interactions = interactions
        self._conditions = conditions
        self._retriever = retriever
        self._queries = queries
        self._limit = fragments_limit

    def collect(self, case: ClinicalCase) -> CaseEvidence:
        drugs = tuple(self._normalizer.normalize_many(case.medication_names))
        inns = [d.inn for d in drugs if d.inn]
        return CaseEvidence(
            case=case,
            drugs=drugs,
            interactions=tuple(self._interactions.detect(inns)),
            conditions=self._conditions.detect(case, inns),
            guidelines=self._retriever.search_many(self._queries.for_case(case), self._limit),
        )
