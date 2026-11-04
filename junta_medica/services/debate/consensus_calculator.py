"""ConsensusCalculator: nivel de acuerdo de una ronda y si hay consenso."""
from junta_medica.models.debate.review import Review
from junta_medica.models.pharmacology.severity import Severity


class ConsensusCalculator:
    def __init__(self, threshold: float):
        self._threshold = threshold

    def evaluate(self, reviews: list[Review]) -> tuple[float, bool]:
        """
        Nivel de acuerdo: el Agente Clínico cuenta como de acuerdo con su propia propuesta y cada revisor suma
        si no objetó. Ej.: 1 objeción de 2 revisores -> (1 + 1) / 3 = 0,67 (redondeado a 2 decimales).

        Hay consenso si el nivel alcanza el umbral Y nadie planteó una objeción GRAVE (de seguridad):
        con 2 revisores, una sola objeción ya da 0,67, y sin esta condición el debate se cerraría sin que el
        Clínico corrija un riesgo para el paciente.
        """
        agreeing = 1 + sum(1 for r in reviews if r.stance.is_agreement)
        level = round(agreeing / (1 + len(reviews)), 2)
        severe = any(o.severity is Severity.SEVERE for r in reviews for o in r.objections)
        return level, level >= self._threshold and not severe
