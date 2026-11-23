"""La respuesta principal: el dictamen del Médico Jefe, o el aviso de evidencia insuficiente (RF11)."""
from junta_medica.config.texts import CHIEF_INSUFFICIENT_EVIDENCE
from junta_medica.services.reports.result_reader import ResultReader
from junta_medica.ui.components.html import chip, esc, render


def verdict_hero(result: ResultReader) -> None:
    if result.abstained:
        render('<div class="jm-hero warning"><div class="jm-hero-label">Evidencia insuficiente</div>'
               '<div class="jm-hero-title">La junta no emite una segunda opinión para este caso</div>'
               f'<div class="jm-hero-text">{esc(result.abstention_reason)}</div></div>')
        return
    verdict = result.verdict or {}
    warning = ""
    if result.insufficient_evidence:
        warning = (f'<div class="jm-hero warning" style="margin-bottom:.6rem"><div class="jm-hero-label">Atención</div>'
                   f'<div class="jm-hero-text">{esc(CHIEF_INSUFFICIENT_EVIDENCE)}</div></div>')
    primary = result.primary_diagnosis
    title = (f'<span class="jm-hero-code">{esc(primary.get("icd10", ""))}</span>{esc(primary.get("name", ""))}'
             if primary else "Sin diagnóstico principal")
    differentials = "".join(chip(f'{d.get("icd10", "")} · {d.get("name", "")}', "teal")
                            for d in result.differential_diagnoses)
    differentials_html = (f'<div style="margin-top:.7rem"><span class="jm-muted">Diagnósticos diferenciales:</span><br>'
                          f'{differentials}</div>') if differentials else ""
    render(f'{warning}<div class="jm-hero"><div class="jm-hero-label">Diagnóstico principal · segunda opinión</div>'
           f'<div class="jm-hero-title">{title}</div>'
           f'<div class="jm-hero-text">{esc(verdict.get("summary", ""))}</div>{differentials_html}</div>')
