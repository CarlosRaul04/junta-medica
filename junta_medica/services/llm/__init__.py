"""
Servicios de IA:
    llm_client.py        -> LLMClient: el único punto por el que los agentes hablan con la IA
    cost_calculator.py -> CostCalculator: costo en dólares de cada llamada
    json_parser.py    -> parse_json(): texto del modelo -> diccionario
    providers/          -> OpenAICompatibleProvider (cualquier API compatible con OpenAI) y MockLLMProvider (sin costo)
"""
