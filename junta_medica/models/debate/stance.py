"""Stance: postura de un agente revisor frente a la propuesta del Agente Clínico."""
from enum import Enum


class Stance(str, Enum):
    AGREE = "agree"                                # de acuerdo
    AGREE_WITH_COMMENTS = "agree_with_comments"    # de acuerdo con observaciones (no bloquea el consenso)
    OBJECTION = "objection"                        # objeción (bloquea el consenso)

    @property
    def is_agreement(self) -> bool:
        return self is not Stance.OBJECTION
