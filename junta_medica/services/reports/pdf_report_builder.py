"""
PdfReportBuilder: arma el informe PDF de una consulta (RF13), con trazabilidad (RF14) y disclaimer (RF17).

Partes: encabezado · datos del caso · dictamen del Médico Jefe (o evidencia insuficiente) · alertas ·
recomendaciones con su fuente · resumen del debate por ronda · trazabilidad y métricas.
"""
import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from junta_medica.models.history.consultation import Consultation
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.date_formatter import DateFormatter
from junta_medica.services.reports.result_reader import ResultReader

NAVY = colors.HexColor("#13293D")
TEAL = colors.HexColor("#0B6E70")
RUST = colors.HexColor("#B4501A")
RED = colors.HexColor("#B42318")
AMBER = colors.HexColor("#B54708")
LIGHT = colors.HexColor("#F2F5F7")
GRID = colors.HexColor("#D0D7DE")

# Caracteres que las fuentes estándar de PDF no tienen
_REPLACEMENTS = {"≥": ">=", "≤": "<=", "→": "->", "–": "-", "•": "-", "µ": "u", "×": "x"}


def _text(value) -> str:
    text = str(value or "")
    for original, replacement in _REPLACEMENTS.items():
        text = text.replace(original, replacement)
    return escape(text)


class PdfReportBuilder:
    def __init__(self, citations: CitationFormatter, dates: DateFormatter, labels: dict, lab_labels: dict[str, str],
                 disclaimer: str, title: str):
        self._citations = citations
        self._dates = dates
        self._labels = labels            # {"severity": {...}, "stance": {...}, "role": {...}, "sex": {...}}
        self._lab_labels = lab_labels    # clave de laboratorio -> nombre con unidad
        self._disclaimer = disclaimer
        self._title = title
        self._styles = self._build_styles()

    def build(self, result: ResultReader, consultation: Consultation, physician: str) -> bytes:
        buffer = io.BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                                     topMargin=30 * mm, bottomMargin=22 * mm,
                                     title=f"{self._title} - {result.case_id}", author=physician)
        story = []
        story += self._case_section(result, consultation, physician)
        story += self._verdict_section(result)
        story += self._alerts_section(result)
        story += self._recommendations_section(result)
        story += self._debate_section(result)
        story += self._traceability_section(result)
        document.build(story, onFirstPage=self._decorate(result, consultation),
                       onLaterPages=self._decorate(result, consultation))
        return buffer.getvalue()

    # ------------------------------------------------------------------ secciones
    def _case_section(self, result: ResultReader, consultation: Consultation, physician: str) -> list:
        case = result.case
        sex = self._labels["sex"].get(case.get("sex"), case.get("sex"))
        meds = ", ".join(f"{m['name']} {m.get('dose', '')}".strip() for m in case.get("medications", []))
        labs = "; ".join(f"{self._lab_labels.get(k, k)}: {v:g}" for k, v in (case.get("lab_results") or {}).items())
        rows = [
            ["Código del caso", result.case_id, "Fecha", self._dates.format(consultation.created_at)],
            ["Edad / sexo", f"{case.get('age')} años · {sex}", "Médico", physician],
            ["Motivo de consulta", case.get("chief_complaint", ""), "", ""],
            ["Síntomas", ", ".join(case.get("symptoms", [])), "", ""],
            ["Antecedentes", ", ".join(case.get("medical_history", [])) or "—", "", ""],
            ["Alergias", ", ".join(case.get("allergies", [])) or "Ninguna registrada", "", ""],
            ["Medicación", meds, "", ""],
            ["Laboratorio", labs or "—", "", ""],
        ]
        data = [[self._p(r[0], "label"), self._p(r[1]), self._p(r[2], "label"), self._p(r[3])] if r[2]
                else [self._p(r[0], "label"), self._p(r[1]), "", ""] for r in rows]
        table = Table(data, colWidths=[32 * mm, 62 * mm, 24 * mm, 56 * mm])
        style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                 ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("BACKGROUND", (2, 0), (2, 1), LIGHT)]
        style += [("SPAN", (1, i), (3, i)) for i in range(2, len(rows))]
        table.setStyle(TableStyle(style))
        return [self._heading("1. Datos del caso"), table, Spacer(1, 6 * mm)]

    def _verdict_section(self, result: ResultReader) -> list:
        story = [self._heading("2. Segunda opinión de la junta médica")]
        if result.abstained:
            story.append(self._box("Evidencia insuficiente", result.abstention_reason, AMBER))
            return story + [Spacer(1, 5 * mm)]
        verdict = result.verdict or {}
        if result.insufficient_evidence:
            story.append(self._box("Evidencia insuficiente",
                                   "El Médico Jefe indicó que las guías no respaldan una recomendación para este "
                                   "caso. Tome lo siguiente con cautela.", AMBER))
            story.append(Spacer(1, 3 * mm))
        primary = result.primary_diagnosis
        if primary:
            story.append(self._box("Diagnóstico principal", f"{primary.get('icd10', '')} · {primary.get('name', '')}",
                                   TEAL))
            story.append(Spacer(1, 3 * mm))
        if result.differential_diagnoses:
            items = "; ".join(f"{d.get('icd10', '')} {d.get('name', '')}" for d in result.differential_diagnoses)
            story.append(self._p(f"<b>Diagnósticos diferenciales:</b> {_text(items)}", raw=True))
        story.append(Spacer(1, 2 * mm))
        story.append(self._p(f"<b>Resumen del Médico Jefe:</b> {_text(verdict.get('summary', ''))}", raw=True))
        for item in result.limitations:
            story.append(self._p(f"<b>No cubierto por las guías:</b> {_text(item)}", raw=True))
        for item in result.disagreements:
            story.append(self._p(f"<font color='#B54708'><b>Discrepancia sin resolver:</b></font> {_text(item)}",
                                 raw=True))
        return story + [Spacer(1, 5 * mm)]

    def _alerts_section(self, result: ResultReader) -> list:
        story = [self._heading("3. Alertas de seguridad de la medicación")]
        if not result.alerts:
            return story + [self._p("No se encontraron interacciones ni contraindicaciones en las tablas."),
                            Spacer(1, 5 * mm)]
        data = [[self._p("Gravedad", "th"), self._p("Alerta", "th"), self._p("Fuente", "th")]]
        backgrounds = []
        for i, alert in enumerate(result.highlighted_alerts + result.other_alerts, start=1):
            severity = self._labels["severity"].get(alert["severity"], alert["severity"])
            data.append([self._p(severity.capitalize(), "bold"), self._p(alert["text"]),
                         self._p("; ".join(self._citations.format(c) for c in alert.get("citations", [])), "small")])
            if alert.get("highlighted"):
                backgrounds.append(("BACKGROUND", (0, i), (0, i), colors.HexColor("#FEE4E2")))
        table = Table(data, colWidths=[24 * mm, 96 * mm, 54 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"), *backgrounds]))
        return story + [table, Spacer(1, 5 * mm)]

    def _recommendations_section(self, result: ResultReader) -> list:
        if not result.recommendations:
            return []
        story = [self._heading("4. Recomendaciones")]
        for number, item in enumerate(result.recommendations, start=1):
            sources = "; ".join(self._citations.format(c) for c in item.get("citations", []))
            text = f"<b>{number}.</b> {_text(item.get('text', ''))}"
            if sources:
                text += f"<br/><font size='8' color='#57606A'>Fuente: {_text(sources)}</font>"
            story.append(self._p(text, raw=True))
        return story + [Spacer(1, 5 * mm)]

    def _debate_section(self, result: ResultReader) -> list:
        if not result.rounds:
            return []
        story = [self._heading("5. Cómo llegó la junta a esta conclusión")]
        data = [[self._p(h, "th") for h in ("Ronda", "Diagnósticos propuestos", "Farmacológico", "Protocolo", "Acuerdo")]]
        for r in result.rounds:
            diagnoses = "<br/>".join(f"{_text(d.get('icd10', ''))} {_text(d.get('name', ''))}"
                                     for d in r["proposal"]["output"].get("diagnoses", []))
            stances = {t["role"]: self._labels["stance"].get(t["output"]["stance"], t["output"]["stance"])
                       for t in r["reviews"]}
            data.append([self._p(str(r["number"]), "bold"), self._p(diagnoses, raw=True),
                         self._p(stances.get("pharmacological", "")), self._p(stances.get("protocol", "")),
                         self._p(f"{r['agreement_level']:.0%}" + (" · consenso" if r["consensus"] else ""))])
        table = Table(data, colWidths=[17 * mm, 69 * mm, 31 * mm, 31 * mm, 26 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return story + [table, Spacer(1, 5 * mm)]

    def _traceability_section(self, result: ResultReader) -> list:
        check = result.citation_check
        invalid = check.get("invalid") or []
        rows = [
            ["Trazabilidad", f"{result.traceability:.0%} de las afirmaciones con cita válida "
                             f"({check.get('cited_claims', 0)}/{check.get('total_claims', 0)})"],
            ["Citas inválidas", ", ".join(invalid) if invalid else "Ninguna"],
            ["Llamadas a la IA", str(result.llm_calls)],
            ["Tiempo de la junta", f"{result.seconds:.0f} s"],
            ["Modelos", ", ".join(result.models) or "—"],
        ]
        table = Table([[self._p(a, "label"), self._p(b)] for a, b in rows], colWidths=[40 * mm, 134 * mm])
        table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, GRID), ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return [KeepTogether([self._heading("6. Trazabilidad y métricas"), table])]

    # ------------------------------------------------------------------ piezas
    def _decorate(self, result: ResultReader, consultation: Consultation):
        def draw(canvas, document):
            width, height = A4
            canvas.saveState()
            canvas.setFillColor(NAVY)
            canvas.rect(0, height - 20 * mm, width, 20 * mm, stroke=0, fill=1)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawString(18 * mm, height - 12 * mm, self._title)
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(width - 18 * mm, height - 12 * mm,
                                   f"{result.case_id} · consulta N.° {consultation.consultation_id}")
            canvas.setFillColor(colors.HexColor("#57606A"))
            canvas.setFont("Helvetica-Oblique", 7.5)
            lines = simpleSplit(self._disclaimer, "Helvetica-Oblique", 7.5, width - 60 * mm)
            for i, line in enumerate(lines):
                canvas.drawString(18 * mm, (12 - 3.5 * i) * mm, line)
            canvas.drawRightString(width - 18 * mm, 12 * mm, f"Página {document.page}")
            canvas.restoreState()
        return draw

    def _heading(self, text: str) -> Paragraph:
        return Paragraph(_text(text), self._styles["h2"])

    def _box(self, title: str, body: str, color) -> Table:
        table = Table([[Paragraph(f"<b>{_text(title)}</b><br/>{_text(body)}", self._styles["box"])]],
                      colWidths=[174 * mm])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return table

    def _p(self, text: str, style: str = "body", raw: bool = False) -> Paragraph:
        return Paragraph(text if raw else _text(text), self._styles[style])

    @staticmethod
    def _build_styles() -> dict[str, ParagraphStyle]:
        body = ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12, alignment=TA_LEFT,
                              spaceAfter=2)
        return {
            "body": body,
            "small": ParagraphStyle("small", parent=body, fontSize=7.5, leading=9.5,
                                    textColor=colors.HexColor("#57606A")),
            "bold": ParagraphStyle("bold", parent=body, fontName="Helvetica-Bold"),
            "label": ParagraphStyle("label", parent=body, fontName="Helvetica-Bold", textColor=NAVY),
            "th": ParagraphStyle("th", parent=body, fontName="Helvetica-Bold", textColor=colors.white),
            "box": ParagraphStyle("box", parent=body, fontSize=10, leading=14),
            "h2": ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12, leading=16,
                                 textColor=TEAL, spaceBefore=2, spaceAfter=4),
        }
