"""ReviewParser: JSON del Agente Farmacológico o de Protocolo -> Review."""
from junta_medica.models.debate.objection import Objection
from junta_medica.models.debate.review import Review
from junta_medica.models.debate.stance import Stance
from junta_medica.services.agents.parsing.field_readers import (
    read_citations, read_cited_items, read_severity, read_text, read_text_list, split_inline_citations,
)


class ReviewParser:
    def __init__(self, stance_synonyms: dict[str, str], unknown_stance: str):
        self._synonyms = stance_synonyms
        self._unknown = Stance(unknown_stance)

    def parse(self, data: dict) -> Review:
        objections = tuple(self._objection(o) for o in self._as_list(data.get("objections")))
        objections = tuple(o for o in objections if o.detail)
        stance = self._stance(data.get("stance"))
        if objections and stance is Stance.AGREE:
            stance = Stance.AGREE_WITH_COMMENTS   # dijo "de acuerdo" pero objetó algo: no se pierde la objeción
        return Review(
            stance=stance,
            objections=objections,
            comments=read_text_list(data.get("comments")),
            additional_alerts=read_cited_items(data.get("additional_alerts")),
        )

    def _stance(self, value) -> Stance:
        text = read_text(value).lower().strip()
        text = self._synonyms.get(text, text)
        try:
            return Stance(text)
        except ValueError:
            return self._unknown

    @staticmethod
    def _objection(value) -> Objection:
        if isinstance(value, dict):
            detail, citations = split_inline_citations(read_text(value.get("detail")), read_citations(value.get("citations")))
            return Objection(read_severity(value.get("severity")), detail, citations)
        detail, citations = split_inline_citations(read_text(value), ())
        return Objection(read_severity(None), detail, citations)

    @staticmethod
    def _as_list(value) -> list:
        if value is None or value == "":
            return []
        return value if isinstance(value, list) else [value]
