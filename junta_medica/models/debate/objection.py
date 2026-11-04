"""Objection: un desacuerdo concreto de un revisor, con su gravedad y su cita."""
from dataclasses import dataclass

from junta_medica.models.pharmacology.severity import Severity


@dataclass(frozen=True)
class Objection:
    severity: Severity        # severe = problema de seguridad del paciente
    detail: str
    citations: tuple[str, ...] = ()
