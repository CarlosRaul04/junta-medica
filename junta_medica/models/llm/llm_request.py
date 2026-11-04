"""LLMRequest: lo que un agente le pide al modelo de lenguaje."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    role: str            # agente que hace la consulta (trazabilidad y modo simulado)
    instructions: str  # el "papel" del agente (mensaje de sistema)
    message: str        # el contenido a analizar
    model: str
