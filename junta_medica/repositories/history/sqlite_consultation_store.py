"""SQLiteConsultationStore: el historial de consultas en SQLite (RF16)."""
from datetime import datetime, timezone

from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.models.history.consultation import Consultation
from junta_medica.models.history.consultation_filter import ConsultationFilter
from junta_medica.models.history.new_consultation import NewConsultation
from junta_medica.repositories.database.sqlite_database import SQLiteDatabase

_SELECT = ("SELECT c.*, u.username FROM consultations c JOIN users u ON u.user_id = c.user_id")


class SQLiteConsultationStore(ConsultationStore):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def add(self, consultation: NewConsultation) -> Consultation:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        c = consultation
        with self._database.connect() as db:
            cursor = db.execute(
                """INSERT INTO consultations (case_id, created_at, user_id, insufficient_evidence, primary_icd10,
                   primary_name, agreement, rounds, severe_alerts, traceability, seconds, llm_calls, models,
                   result_key, report_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (c.case_id, created_at, c.user_id, int(c.insufficient_evidence), c.primary_icd10, c.primary_name,
                 c.agreement, c.rounds, c.severe_alerts, c.traceability, c.seconds, c.llm_calls, c.models,
                 c.result_key, c.report_key),
            )
            consultation_id = cursor.lastrowid
        return self.get(consultation_id)

    def get(self, consultation_id: int) -> Consultation | None:
        with self._database.connect() as db:
            row = db.execute(f"{_SELECT} WHERE c.consultation_id = ?", (consultation_id,)).fetchone()
        return self._to_consultation(row) if row else None

    def search(self, criteria: ConsultationFilter) -> list[Consultation]:
        sql, params = f"{_SELECT} WHERE 1 = 1", []
        if criteria.user_id is not None:
            sql += " AND c.user_id = ?"
            params.append(criteria.user_id)
        if criteria.text.strip():
            sql += " AND (c.case_id LIKE ? OR c.primary_icd10 LIKE ? OR c.primary_name LIKE ?)"
            params += [f"%{criteria.text.strip()}%"] * 3
        if criteria.insufficient_evidence is not None:
            sql += " AND c.insufficient_evidence = ?"
            params.append(int(criteria.insufficient_evidence))
        sql += " ORDER BY c.consultation_id DESC LIMIT ?"
        params.append(criteria.limit)
        with self._database.connect() as db:
            return [self._to_consultation(row) for row in db.execute(sql, params)]

    def set_report_key(self, consultation_id: int, report_key: str) -> None:
        with self._database.connect() as db:
            db.execute("UPDATE consultations SET report_key = ? WHERE consultation_id = ?",
                       (report_key, consultation_id))

    @staticmethod
    def _to_consultation(row) -> Consultation:
        return Consultation(
            consultation_id=row["consultation_id"], case_id=row["case_id"], created_at=row["created_at"],
            user_id=row["user_id"], username=row["username"],
            insufficient_evidence=bool(row["insufficient_evidence"]), primary_icd10=row["primary_icd10"],
            primary_name=row["primary_name"], agreement=row["agreement"], rounds=row["rounds"],
            severe_alerts=row["severe_alerts"], traceability=row["traceability"], seconds=row["seconds"],
            llm_calls=row["llm_calls"], models=row["models"], result_key=row["result_key"],
            report_key=row["report_key"],
        )
