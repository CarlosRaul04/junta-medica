"""CatalogDrug: un medicamento del catálogo, con todos los nombres por los que se le conoce."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogDrug:
    inn: str                           # nombre oficial en español (Denominación Común Internacional)
    drug_class: str                         # grupo terapéutico
    atc: str                           # código ATC de la OMS
    synonyms: tuple[str, ...] = ()    # otras formas de escribirlo
    brands: tuple[str, ...] = ()       # nombres comerciales
    english_names: tuple[str, ...] = ()   # nombre(s) en inglés; en combinaciones, cada componente
    guidelines: tuple[str, ...] = ()        # guías que lo mencionan
