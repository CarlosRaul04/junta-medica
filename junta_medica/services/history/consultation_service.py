"""
ConsultationService: registra cada consulta en el historial y recupera sus archivos (RF13, RF14, RF16).

Al terminar la junta guarda: el JSON completo (FileStorage), el resumen (ConsultationStore) y el informe PDF.
Un médico solo ve sus consultas; el administrador ve todas (RF15).
"""
import json
from datetime import datetime

from junta_medica.exceptions import AccessDeniedError
from junta_medica.interfaces.consultation_store import ConsultationStore
from junta_medica.interfaces.file_storage import FileStorage
from junta_medica.models.debate.debate_result import DebateResult
from junta_medica.models.history.consultation import Consultation
from junta_medica.models.history.consultation_filter import ConsultationFilter
from junta_medica.models.users.user import User
from junta_medica.repositories.debate.debate_result_serializer import DebateResultSerializer
from junta_medica.services.history.consultation_summary import consultation_summary
from junta_medica.services.reports.pdf_report_builder import PdfReportBuilder
from junta_medica.services.reports.result_reader import ResultReader


class ConsultationService:
    def __init__(self, store: ConsultationStore, files: FileStorage, serializer: DebateResultSerializer,
                 reports: PdfReportBuilder, results_prefix: str, reports_prefix: str,
                 json_type: str, pdf_type: str, insufficient_label: str):
        self._store = store
        self._files = files
        self._serializer = serializer
        self._reports = reports
        self._results_prefix = results_prefix
        self._reports_prefix = reports_prefix
        self._json_type = json_type
        self._pdf_type = pdf_type
        self._insufficient_label = insufficient_label

    def record(self, result: DebateResult, user: User) -> Consultation:
        data = self._serializer.to_dict(result)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"{result.case_id}_{stamp}"
        result_key = self._files.save(f"{self._results_prefix}/{name}.json",
                                      json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                                      self._json_type)
        consultation = self._store.add(
            consultation_summary(ResultReader(data), user.user_id, result_key, self._insufficient_label))
        pdf = self._reports.build(ResultReader(data), consultation, user.full_name)
        report_key = self._files.save(f"{self._reports_prefix}/{name}.pdf", pdf, self._pdf_type)
        self._store.set_report_key(consultation.consultation_id, report_key)
        return self._store.get(consultation.consultation_id)

    def search(self, user: User, text: str = "", insufficient_evidence: bool | None = None,
               all_users: bool = False) -> list[Consultation]:
        user_id = None if (all_users and user.role.can_see_all_history) else user.user_id
        return self._store.search(ConsultationFilter(user_id, text, insufficient_evidence))

    def get(self, user: User, consultation_id: int) -> Consultation:
        consultation = self._store.get(consultation_id)
        if not consultation:
            raise AccessDeniedError("Esa consulta no existe.")
        if consultation.user_id != user.user_id and not user.role.can_see_all_history:
            raise AccessDeniedError("Esa consulta es de otro médico.")
        return consultation

    def load_result(self, consultation: Consultation) -> ResultReader | None:
        content = self._files.load(consultation.result_key)
        return ResultReader(json.loads(content.decode("utf-8"))) if content else None

    def load_report(self, consultation: Consultation, user_name: str) -> bytes | None:
        """El PDF guardado; si falta (ej. consulta antigua), se vuelve a generar desde el JSON."""
        stored = self._files.load(consultation.report_key) if consultation.report_key else None
        if stored:
            return stored
        result = self.load_result(consultation)
        return self._reports.build(result, consultation, user_name) if result else None
