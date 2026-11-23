"""Fuentes consultadas y trazabilidad: fragmentos de guías, citas inválidas y detalle por agente (RF14)."""
import pandas as pd
import streamlit as st

from junta_medica.config.texts import ROLE_LABELS
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.result_reader import ResultReader

TRACEABILITY_GOAL = 0.90   # meta del documento del curso


def sources_view(result: ResultReader, citations: CitationFormatter) -> None:
    check = result.citation_check
    st.markdown("#### Trazabilidad")
    st.progress(min(result.traceability, 1.0),
                text=f"{result.traceability:.0%} de las afirmaciones tienen una cita válida "
                     f"({check.get('cited_claims', 0)} de {check.get('total_claims', 0)}) · meta {TRACEABILITY_GOAL:.0%}")
    invalid = check.get("invalid") or []
    if invalid:
        st.error("Citas que no existen en lo que se entregó a los agentes (inventadas): " + ", ".join(invalid))
    else:
        st.caption("Ninguna cita inventada: todas existen en las guías, tablas o reglas que recibieron los agentes.")

    st.markdown("#### Fragmentos de guías consultados")
    chunks = result.guideline_chunks
    if not chunks:
        st.caption("No se recuperaron fragmentos.")
    for item in chunks:
        chunk = item["chunk"]
        citation = f"{chunk['document_id']}:p{chunk['start_page']}" + (
            f"-{chunk['end_page']}" if chunk["end_page"] != chunk["start_page"] else "")
        with st.expander(f"{citations.format(citation)} · similitud {item['similarity']:.2f}"):
            if chunk.get("title"):
                st.markdown(f"**{chunk['title']}**")
            st.write(chunk["text"])

    st.markdown("#### Detalle técnico por agente")
    rows = [{
        "Agente": ROLE_LABELS.get(t["role"], t["role"]),
        "Ronda": str(t["round_number"] or "final"),
        "Modelo": t["llm"]["model"],
        "Tokens (entrada / salida)": f"{t['llm']['input_tokens']} / {t['llm']['output_tokens']}",
        "Tiempo (s)": round(t["llm"]["seconds"], 1),
        "Intentos": t["llm"]["attempts"],
    } for t in result.turns]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    else:
        st.caption("No se llamó a la IA.")
