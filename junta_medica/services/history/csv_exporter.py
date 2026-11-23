"""CsvExporter: exporta el historial a CSV (RF16). Con BOM para que Excel muestre bien las tildes."""
import csv
import io

from junta_medica.models.history.consultation import Consultation

COLUMNS = {
    "consultation_id": "N.° consulta", "case_id": "Código del caso", "created_at": "Fecha (UTC)",
    "username": "Usuario", "insufficient_evidence": "Evidencia insuficiente", "primary_icd10": "CIE-10",
    "primary_name": "Diagnóstico principal", "agreement": "Acuerdo final", "rounds": "Rondas",
    "severe_alerts": "Alertas graves", "traceability": "Trazabilidad", "seconds": "Tiempo (s)",
    "llm_calls": "Llamadas a la IA", "models": "Modelos",
}


class CsvExporter:
    def export(self, consultations: list[Consultation]) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(COLUMNS.values())
        for c in consultations:
            row = []
            for field in COLUMNS:
                value = getattr(c, field)
                if isinstance(value, bool):
                    value = "sí" if value else "no"
                elif field in ("agreement", "traceability"):
                    value = f"{value:.0%}"
                row.append(value)
            writer.writerow(row)
        return ("﻿" + buffer.getvalue()).encode("utf-8")
