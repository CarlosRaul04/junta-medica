"""Review: la revisión del Agente Farmacológico o del Agente de Protocolo sobre la propuesta clínica."""
from dataclasses import dataclass

from junta_medica.models.debate.cited_item import CitedItem
from junta_medica.models.debate.objection import Objection
from junta_medica.models.debate.stance import Stance


@dataclass(frozen=True)
class Review:
    stance: Stance
    objections: tuple[Objection, ...] = ()
    comments: tuple[str, ...] = ()
    additional_alerts: tuple[CitedItem, ...] = ()   # alertas que el agente agrega (con cita) a las de la tabla
