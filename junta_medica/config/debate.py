"""Parámetros del ciclo de debate entre agentes."""

MAX_ROUNDS = 3              # rondas máximas de debate
CONSENSUS_THRESHOLD = 0.67      # proporción mínima de acuerdo

DEBATE_ROLES = ["clinical", "pharmacological", "protocol"]
CHIEF_ROLE = "chief"

VALID_STANCES = ["agree", "agree_with_comments", "objection"]

# --- Lectura de las respuestas de los agentes (tolerante: los modelos gratuitos a veces responden en español) ---
STANCE_SYNONYMS = {
    "de acuerdo": "agree", "de_acuerdo": "agree", "acuerdo": "agree", "aprobado": "agree",
    "de acuerdo con observaciones": "agree_with_comments", "de_acuerdo_con_observaciones": "agree_with_comments",
    "con observaciones": "agree_with_comments", "agree with comments": "agree_with_comments",
    "objecion": "objection", "objeción": "objection", "desacuerdo": "objection", "disagree": "objection",
}
UNKNOWN_STANCE = "objection"        # postura ilegible -> se trata como objeción (lo más prudente)
VALID_LIKELIHOODS = ["high", "medium", "low"]
LIKELIHOOD_SYNONYMS = {"alta": "high", "media": "medium", "moderada": "medium", "baja": "low"}
DEFAULT_LIKELIHOOD = "medium"
MAX_DIAGNOSES = 3                   # el Clínico propone un top-3 (CP04)
MAX_DIFFERENTIALS = 2               # el Jefe da 1 principal + hasta 2 diferenciales

# --- Contexto que recibe cada agente ---
CLINICAL_FRAGMENTS = 6              # fragmentos de guía para el Clínico (búsqueda por el caso)
PROTOCOL_FRAGMENTS = 6              # fragmentos para el de Protocolo (búsqueda por la propuesta)
FRAGMENT_MAX_CHARS = 1200           # cada fragmento se recorta a este largo dentro del mensaje
QUERY_MAX_CHARS = 400               # largo máximo de cada consulta al buscador

# --- Abstención (RF11) ---
# Si el buscador no encuentra evidencia suficiente para el caso, el sistema NO debate: se abstiene
# (ahorra llamadas y evita una segunda opinión sin respaldo). Las alertas de seguridad se informan igual.
ABSTAIN_WITHOUT_DEBATE = True
