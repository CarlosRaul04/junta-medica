"""ConsultationStore: el historial de consultas (implementaciones: SQLite local, MongoDB en AWS)."""
from abc import ABC, abstractmethod

from junta_medica.models.history.consultation import Consultation
from junta_medica.models.history.consultation_filter import ConsultationFilter
from junta_medica.models.history.new_consultation import NewConsultation


class ConsultationStore(ABC):
    @abstractmethod
    def add(self, consultation: NewConsultation) -> Consultation:
        ...

    @abstractmethod
    def get(self, consultation_id: int) -> Consultation | None:
        ...

    @abstractmethod
    def search(self, criteria: ConsultationFilter) -> list[Consultation]:
        """De la más reciente a la más antigua."""

    @abstractmethod
    def set_report_key(self, consultation_id: int, report_key: str) -> None:
        ...
