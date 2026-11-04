"""Textos fijos que se muestran al usuario."""

DISCLAIMER = (
    "Este informe es una herramienta de apoyo a la decisión clínica y no "
    "reemplaza el criterio del médico tratante, quien conserva la "
    "responsabilidad final."
)

SEVERITY_LABELS = {"severe": "grave", "moderate": "moderada", "mild": "leve", "unknown": "sin clasificar"}
STANCE_LABELS = {"agree": "de acuerdo", "agree_with_comments": "de acuerdo con observaciones", "objection": "objeción"}
ROLE_LABELS = {
    "clinical": "Agente Clínico", "pharmacological": "Agente Farmacológico",
    "protocol": "Agente de Protocolo", "chief": "Médico Jefe",
}
ABSTENTION_MESSAGE = (
    "Evidencia insuficiente: las guías de práctica clínica de la base de conocimiento no cubren este caso. "
    "El sistema no emite una segunda opinión diagnóstica ni terapéutica; se recomienda la evaluación por la "
    "especialidad correspondiente. Las alertas de seguridad de la medicación se informan igualmente."
)
