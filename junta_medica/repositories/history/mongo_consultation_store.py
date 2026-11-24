"""
MongoConsultationStore: el historial de consultas en MongoDB (colección consultations) (RF16).

Cada documento guarda también el nombre de usuario (no cambia nunca), así no hace falta "unir" colecciones.
"""
import dataclasses
import re
from datetime import datetime, timezone

from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.models.history.consultation import Consultation
from junta_medica.models.history.consultation_filter import ConsultationFilter
from junta_medica.models.history.new_consultation import NewConsultation
from junta_medica.repositories.database.mongo_database import MongoDatabase

_FIELDS = [f.name for f in dataclasses.fields(Consultation)]


class MongoConsultationStore(ConsultationStore):
    def __init__(self, database: MongoDatabase):
        self._database = database

    def add(self, consultation: NewConsultation) -> Consultation:
        user = self._database.users.find_one({"user_id": consultation.user_id}) or {}
        document = {
            **dataclasses.asdict(consultation),
            "consultation_id": self._database.next_id("consultations"),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "username": user.get("username", ""),
        }
        self._database.consultations.insert_one(document)
        return self._to_consultation(document)

    def get(self, consultation_id: int) -> Consultation | None:
        document = self._database.consultations.find_one({"consultation_id": consultation_id})
        return self._to_consultation(document) if document else None

    def search(self, criteria: ConsultationFilter) -> list[Consultation]:
        query: dict = {}
        if criteria.user_id is not None:
            query["user_id"] = criteria.user_id
        if criteria.text.strip():
            pattern = {"$regex": re.escape(criteria.text.strip()), "$options": "i"}
            query["$or"] = [{"case_id": pattern}, {"primary_icd10": pattern}, {"primary_name": pattern}]
        if criteria.insufficient_evidence is not None:
            query["insufficient_evidence"] = criteria.insufficient_evidence
        cursor = self._database.consultations.find(query).sort("consultation_id", -1).limit(criteria.limit)
        return [self._to_consultation(d) for d in cursor]

    def set_report_key(self, consultation_id: int, report_key: str) -> None:
        self._database.consultations.update_one({"consultation_id": consultation_id},
                                                {"$set": {"report_key": report_key}})

    @staticmethod
    def _to_consultation(document: dict) -> Consultation:
        return Consultation(**{field: document.get(field, "") for field in _FIELDS})
