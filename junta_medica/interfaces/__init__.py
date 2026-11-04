"""
INTERFACES: contratos que cumplen las piezas intercambiables. Quien usa una interfaz no sabe qué implementación hay detrás.

    llm_provider.py      -> LLMProvider      (implementaciones: OpenAI, simulado)
    validation_rule.py   -> ValidationRule   (implementaciones: reglas de campos, clínicas, privacidad)
    condition_criterion.py -> ConditionCriterion (implementaciones: laboratorio, edad, antecedente)
    embedding_model.py  -> EmbeddingModel  (implementaciones: e5 local, falso de pruebas)
    vector_store.py  -> VectorStore  (implementaciones: ChromaDB, memoria de pruebas)
"""
