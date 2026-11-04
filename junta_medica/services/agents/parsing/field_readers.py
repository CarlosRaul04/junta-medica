"""
Funciones para leer campos del JSON de un agente sin romperse si el modelo se equivoca de tipo
(ej. una lista donde iba un texto, una cita suelta en vez de una lista, campos que faltan).
"""
import re

from junta_medica.models.debate.cited_item import CitedItem
from junta_medica.models.pharmacology.severity import Severity

_CITATION_IN_BRACKETS = re.compile(r"^\[(.*)\]$")
_CITATION_INSIDE_TEXT = re.compile(r"\s*\[([a-z0-9_]+:[A-Za-z0-9_.-]+)\]")   # "... potasemia. [gpc_ic:p23-24]"


def read_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(read_text(v) for v in value).strip()
    return _remove_stray_closers(str(value).strip())


def _remove_stray_closers(text: str) -> str:
    """Algunos modelos dejan un "}" o "]" suelto al final del texto (ej. "...frecuencia cardíaca.}")."""
    while text and text[-1] in "}]" and text.count(text[-1]) > text.count("{" if text[-1] == "}" else "["):
        text = text[:-1].rstrip()
    return text


def read_text_list(value) -> tuple[str, ...]:
    if value is None or value == "":
        return ()
    if not isinstance(value, list):
        value = [value]
    return tuple(t for t in (read_text(v) for v in value) if t)


def read_citations(value) -> tuple[str, ...]:
    """Acepta ["gpc_ic:p23"], "gpc_ic:p23", "[gpc_ic:p23]" o "gpc_ic:p23, ft_x:p5"."""
    raw = []
    for item in read_text_list(value):
        raw += [part.strip() for part in item.split(",")]
    cleaned = []
    for citation in raw:
        match = _CITATION_IN_BRACKETS.match(citation)
        citation = (match.group(1) if match else citation).strip().strip("'\"")
        if citation and citation not in cleaned:
            cleaned.append(citation)
    return tuple(cleaned)


def read_cited_items(value) -> tuple[CitedItem, ...]:
    """Lista de {"text": ..., "citations": [...]}; un texto suelto se acepta como ítem sin citas."""
    if value is None:
        return ()
    if not isinstance(value, list):
        value = [value]
    items = []
    for entry in value:
        if isinstance(entry, dict):
            text = read_text(entry.get("text") or entry.get("detail") or entry.get("action"))
            citations = read_citations(entry.get("citations"))
        else:
            text, citations = read_text(entry), ()
        text, citations = split_inline_citations(text, citations)
        if text:
            items.append(CitedItem(text, citations))
    return tuple(items)


def split_inline_citations(text: str, citations: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    """Si el modelo escribió la cita dentro del texto ("... [gpc_ic:p23]"), la pasa a la lista de citas."""
    found = _CITATION_INSIDE_TEXT.findall(text)
    if not found:
        return text, citations
    clean = _CITATION_INSIDE_TEXT.sub("", text).strip()
    return clean, tuple(dict.fromkeys([*citations, *found]))


def read_severity(value, default: Severity = Severity.MODERATE) -> Severity:
    text = read_text(value).lower()
    synonyms = {"grave": "severe", "alta": "severe", "high": "severe", "moderada": "moderate", "leve": "mild"}
    text = synonyms.get(text, text)
    try:
        return Severity(text)
    except ValueError:
        return default


def read_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def read_bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "sí", "si", "yes", "1")
    return bool(value)
