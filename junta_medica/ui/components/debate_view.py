"""El debate ronda por ronda: qué propuso el Agente Clínico y qué dijeron los revisores."""
import streamlit as st

from junta_medica.config.texts import LIKELIHOOD_LABELS, ROLE_LABELS, SEVERITY_LABELS, STANCE_LABELS
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.result_reader import ResultReader
from junta_medica.ui.components.citation_list import sources_html
from junta_medica.ui.components.html import chip, esc, render

_STANCE_TONES = {"agree": "green", "agree_with_comments": "teal", "objection": "red"}
_LIKELIHOOD_TONES = {"high": "teal", "medium": "amber", "low": "gray"}


def debate_view(result: ResultReader, citations: CitationFormatter) -> None:
    if not result.rounds:
        st.info("No hubo debate: el sistema se abstuvo porque las guías no cubren el caso.")
        return
    total = len(result.rounds)
    for r in result.rounds:
        consensus = chip("Consenso", "green") if r["consensus"] else chip("Sin consenso", "amber")
        title = f"Ronda {r['number']} de {total} · acuerdo {r['agreement_level']:.0%}"
        with st.expander(title, expanded=r["number"] == total):
            render(consensus)
            _proposal(r["proposal"]["output"], r["number"], citations)
            columns = st.columns(len(r["reviews"]))
            for column, turn in zip(columns, r["reviews"]):
                with column:
                    _review(turn["role"], turn["output"], citations)


def _proposal(proposal: dict, number: int, citations: CitationFormatter) -> None:
    st.markdown(f"**{ROLE_LABELS['clinical']}** · {'propuesta inicial' if number == 1 else 'propuesta corregida'}")
    for answer in proposal.get("response_to_objections") or []:
        st.caption(f"↳ Responde a las objeciones: {answer}")
    for d in proposal.get("diagnoses", []):
        likelihood = d.get("likelihood", "")
        render(f'<div class="jm-card"><h4><span class="jm-chip teal">{esc(d.get("icd10", ""))}</span> '
               f'{esc(d.get("name", ""))} {chip("probabilidad " + LIKELIHOOD_LABELS.get(likelihood, likelihood), _LIKELIHOOD_TONES.get(likelihood, "gray"))}</h4>'
               f'<p>{esc(d.get("rationale", ""))}</p>{sources_html(d.get("citations", []), citations)}</div>')
    plan = proposal.get("plan") or []
    if plan:
        st.markdown("**Plan propuesto**")
        for item in plan:
            render(f'<div style="margin-bottom:.35rem">• {esc(item.get("text", ""))}'
                   f'{sources_html(item.get("citations", []), citations)}</div>')


def _review(role: str, review: dict, citations: CitationFormatter) -> None:
    stance = review.get("stance", "")
    items = []
    for objection in review.get("objections") or []:
        severity = SEVERITY_LABELS.get(objection.get("severity"), objection.get("severity"))
        items.append(f'<li><b>Objeción {esc(severity)}:</b> {esc(objection.get("detail", ""))}'
                     f'{sources_html(objection.get("citations", []), citations)}</li>')
    for comment in review.get("comments") or []:
        items.append(f"<li>{esc(comment)}</li>")
    for alert in review.get("additional_alerts") or []:
        items.append(f'<li><b>Alerta:</b> {esc(alert.get("text", ""))}'
                     f'{sources_html(alert.get("citations", []), citations)}</li>')
    body = f"<ul>{''.join(items)}</ul>" if items else '<div class="jm-muted">Sin observaciones.</div>'
    render(f'<div class="jm-agent"><div class="jm-agent-head"><span class="jm-agent-name">{esc(ROLE_LABELS.get(role, role))}</span>'
           f'{chip(STANCE_LABELS.get(stance, stance), _STANCE_TONES.get(stance, "gray"))}</div>{body}</div>')
