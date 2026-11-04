"""Arma los repositorios y servicios de farmacología con las rutas y parámetros de config/."""
from junta_medica.config import pharmacology as config
from junta_medica.config import paths
from junta_medica.models.pharmacology.condition_rule import CriterionType
from junta_medica.repositories.pharmacology.interaction_repository import InteractionRepository
from junta_medica.repositories.pharmacology.drug_repository import DrugRepository
from junta_medica.repositories.pharmacology.condition_rule_repository import ConditionRuleRepository
from junta_medica.services.pharmacology.condition_criteria.history_criterion import HistoryCriterion
from junta_medica.services.pharmacology.condition_criteria.age_criterion import AgeCriterion
from junta_medica.services.pharmacology.condition_criteria.lab_criterion import LabCriterion
from junta_medica.services.pharmacology.drug_normalizer import DrugNormalizer
from junta_medica.services.pharmacology.condition_checker import ConditionChecker
from junta_medica.services.pharmacology.interaction_checker import InteractionChecker


def create_drug_repository() -> DrugRepository:
    return DrugRepository(paths.DRUGS_PATH, config.LIST_SEPARATOR, config.EMPTY_VALUE)


def create_interaction_repository() -> InteractionRepository:
    return InteractionRepository(paths.INTERACTIONS_PATH)


def create_drug_normalizer() -> DrugNormalizer:
    return DrugNormalizer(
        create_drug_repository(),
        config.NAME_SIMILARITY_THRESHOLD,
        config.MIN_LENGTH_FOR_FUZZY,
        config.SALTS_TO_IGNORE,
    )


def create_interaction_checker() -> InteractionChecker:
    return InteractionChecker(
        create_interaction_repository().read_all(),
        config.REPORTED_SEVERITIES,
        config.HIGHLIGHTED_SEVERITIES,
    )


def create_condition_checker() -> ConditionChecker:
    return ConditionChecker(
        rules=ConditionRuleRepository(paths.CONDITION_RULES_PATH).read_all(),
        criteria={
            CriterionType.LAB: LabCriterion(),
            CriterionType.AGE: AgeCriterion(),
            CriterionType.HISTORY: HistoryCriterion(config.LIST_SEPARATOR),
        },
        reported_severities=config.REPORTED_SEVERITIES,
        highlighted_severities=config.HIGHLIGHTED_SEVERITIES,
    )
