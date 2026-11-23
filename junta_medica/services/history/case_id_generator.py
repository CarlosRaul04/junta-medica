"""CaseIdGenerator: propone el siguiente código de caso libre (CASO-019, CASO-020...) para no escribirlo a mano."""
import re

from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.models.history.consultation_filter import ConsultationFilter


class CaseIdGenerator:
    def __init__(self, store: ConsultationStore, reserved_ids: list[str], prefix: str, digits: int):
        self._store = store
        self._reserved = reserved_ids        # códigos de los casos simulados (data/cases/)
        self._prefix = prefix
        self._digits = digits
        self._number = re.compile(rf"^{re.escape(prefix)}(\d+)$")

    def next_id(self) -> str:
        used = self._reserved + [c.case_id for c in self._store.search(ConsultationFilter(limit=100_000))]
        numbers = [int(m.group(1)) for m in map(self._number.match, used) if m]
        return f"{self._prefix}{(max(numbers, default=0) + 1):0{self._digits}d}"
