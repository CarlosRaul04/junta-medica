"""RawLLMResponse (lo que devuelve el proveedor tal cual) y LLMResponse (ya validada, con métricas)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RawLLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    is_mock: bool = False


@dataclass(frozen=True)
class LLMResponse:
    role: str
    model: str
    data: dict
    input_tokens: int
    output_tokens: int
    cost_usd: float
    seconds: float
    attempts: int
    is_mock: bool
