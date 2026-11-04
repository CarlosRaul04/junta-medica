"""Limpieza de nombres de medicamentos para poder compararlos: minúsculas, sin tildes, sin dosis ni sales."""
import re
import unicodedata

# dosis y concentraciones: "50 mg", "875/125 mg", "100 UI/ml", "5 mg/ml"
_NUMBER = r"\d+(?:[.,]\d+)?"
_UNIT = r"(?:mg|g|mcg|ug|ui|u|ml|%)"
_DOSE = re.compile(rf"\b{_NUMBER}(?:\s*/\s*{_NUMBER})*\s*{_UNIT}(?:\s*/\s*(?:ml|g|dosis|h|dia))?(?=\s|$|[),;])")
_PARENTHESES = re.compile(r"\(.*?\)")
_COMBINATION = re.compile(r"\s*(\+|/)\s*")
_INVALID_CHARS = re.compile(r"[^a-z0-9/\- ]")
_WHITESPACE = re.compile(r"\s+")


def remove_accents(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def clean_drug_name(name: str, salts_to_ignore: list[str]) -> str:
    """'Losartán Potásico 50 mg' -> 'losartan' · 'Amoxicilina + Ácido clavulánico' -> 'amoxicilina/acido clavulanico'"""
    text = remove_accents(name.lower())
    text = _PARENTHESES.sub(" ", text)
    text = _DOSE.sub(" ", text)
    text = _COMBINATION.sub("/", text)
    text = _INVALID_CHARS.sub(" ", text)
    words = [p for p in _WHITESPACE.split(text) if p and p not in salts_to_ignore]
    return " ".join(words).replace(" / ", "/").strip(" /")
