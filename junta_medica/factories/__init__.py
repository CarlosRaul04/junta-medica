"""
FABRICAS: el ÚNICO lugar que arma los objetos y los conecta entre sí (como Program.cs en ASP.NET).
Leen la configuración (config/) y entregan servicios listos para usar.

    llm_factory.py          -> create_llm_client()
    knowledge_factory.py -> create_indexer(), create_retriever()
    debate_factory.py      -> create_debate_orchestrator(), create_debate_result_repository()
    case_factory.py        -> create_case_validator(), create_case_loader(), create_case_repository()
    diagnosis_factory.py   -> create_icd10_repository()
    pharmacology_factory.py -> create_drug_repository(), create_drug_normalizer(),
                               create_interaction_checker(), create_condition_checker()
"""
