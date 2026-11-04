"""Convierte el texto devuelto por el modelo en un diccionario de Python."""
import json
import re

from junta_medica.exceptions import InvalidResponseError

_MARKDOWN_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_THINKING_BLOCK = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)  # modelos "de razonamiento"


def parse_json(text: str) -> dict:
    """
    Acepta JSON puro o "ensuciado" como lo devuelven muchos modelos gratuitos:
    con ```json, con un bloque <think>...</think> o con texto antes/después del objeto.
    """
    cleaned_text = _MARKDOWN_FENCE.sub("", _THINKING_BLOCK.sub("", text).strip())
    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        data = _extract_object(cleaned_text, error)
    if not isinstance(data, dict):
        raise InvalidResponseError("Se esperaba un objeto JSON ({...}), no una lista ni un valor suelto.")
    return data


def _extract_object(text: str, original_error: json.JSONDecodeError):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise InvalidResponseError(f"JSON inválido: {original_error}") from original_error
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise InvalidResponseError(f"JSON inválido: {error}") from error
