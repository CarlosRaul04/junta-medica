"""
Variables de entorno (secretos, proveedor y modelos de IA). Se leen del archivo .env.

El sistema funciona con CUALQUIER proveedor compatible con la API de OpenAI
(OpenAI, OpenRouter, Groq, Google Gemini, Ollama local...). Ver .env.ejemplo.
"""
import os

from dotenv import load_dotenv

from junta_medica.config.debate import CHIEF_ROLE, DEBATE_ROLES
from junta_medica.config.paths import ENV_PATH

load_dotenv(ENV_PATH)


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip() == "1"


# 1 = respuestas de ejemplo (data/mock_responses/), sin internet ni costo. 0 = llama al proveedor real.
MOCK_MODE = _flag("MOCK_MODE", "1")

# --- Proveedor ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()   # vacío = OpenAI oficial
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()     # Ollama local no necesita clave

# --- Modelos ---
AGENT_MODEL = os.getenv("AGENT_MODEL", "").strip()   # para Clínico, Farmacológico y Protocolo
CHIEF_MODEL = os.getenv("CHIEF_MODEL", "").strip()   # para el Médico Jefe
# Opcional: un modelo distinto por agente (CLINICAL_MODEL, PHARMACOLOGICAL_MODEL, PROTOCOL_MODEL).
ROLE_MODEL_OVERRIDES = {
    role: os.getenv(f"{role.upper()}_MODEL", "").strip() for role in DEBATE_ROLES + [CHIEF_ROLE]
}

# --- Compatibilidad (algunos modelos gratuitos no soportan todo) ---
LLM_JSON_MODE = _flag("LLM_JSON_MODE", "1")                    # 0 si el proveedor rechaza response_format
LLM_MERGE_SYSTEM_PROMPT = _flag("LLM_MERGE_SYSTEM_PROMPT", "0")  # 1 si el modelo no acepta mensaje "system"
