"""
Agentes con IA (cada uno arma su mensaje, llama al LLMClient y lee la respuesta):
    clinical_agent.py        -> ClinicalAgent: propone diagnósticos (CIE-10) y plan
    pharmacological_agent.py -> PharmacologicalAgent: revisa la seguridad de la medicación
    protocol_agent.py        -> ProtocolAgent: revisa el cumplimiento de las guías
    chief_agent.py           -> ChiefAgent: redacta la segunda opinión final
    context/                 -> convierten el caso y la evidencia en texto para el mensaje
    parsing/                 -> convierten el JSON de la IA en modelos (tolerantes a errores)
"""
