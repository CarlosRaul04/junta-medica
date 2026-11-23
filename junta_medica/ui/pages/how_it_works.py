"""Cómo funciona: los agentes, el proceso, las fuentes, los límites y la configuración actual."""
import streamlit as st

from junta_medica.config.texts import ROLE_LABELS
from junta_medica.ui import dependencies
from junta_medica.ui.components.html import esc, render
from junta_medica.ui.components.page_header import page_header

AGENTS = [
    ("clinical", "Propone hasta 3 diagnósticos (CIE-10) y un plan, citando las guías. En la ronda 1 no ve a nadie; "
                 "desde la ronda 2 corrige con las objeciones."),
    ("pharmacological", "Revisa la medicación con la tabla de interacciones (DDInter y fichas técnicas) y las reglas "
                        "por función renal, edad o antecedentes."),
    ("protocol", "Comprueba que la propuesta siga las guías de práctica clínica y que las citas digan lo que se afirma."),
    ("chief", "Lee todo el debate y escribe la segunda opinión: diagnóstico, recomendaciones y discrepancias."),
]
STEPS = [
    "**Herramientas sin IA**: reconoce los medicamentos, busca interacciones y contraindicaciones, y recupera "
    "los fragmentos de guía más parecidos al caso.",
    "**¿Las guías cubren el caso?** Si ningún fragmento es lo bastante parecido, el sistema se abstiene "
    "(evidencia insuficiente) sin gastar llamadas a la IA.",
    "**Debate**: el Clínico propone; el Farmacológico y el de Protocolo revisan. Hay consenso con 2 de 3 de "
    "acuerdo y ninguna objeción grave. Si no, otra ronda (máximo 3).",
    "**Dictamen**: el Médico Jefe integra todo. Las alertas de las tablas siempre aparecen, aunque la IA no las "
    "mencione.",
    "**Verificación**: se revisa que cada cita exista en lo que se entregó a los agentes (trazabilidad).",
]


def page() -> None:
    page_header("Ayuda", "Cómo funciona la junta médica",
                "Cuatro agentes de IA, cada uno con un rol y con información distinta, debaten tu caso.")
    columns = st.columns(4)
    for column, (role, text) in zip(columns, AGENTS):
        with column:
            render(f'<div class="jm-card" style="min-height:12rem"><h4>{esc(ROLE_LABELS[role])}</h4>'
                   f'<p>{esc(text)}</p></div>')
    st.markdown("### El proceso")
    for number, text in enumerate(STEPS, start=1):
        st.markdown(f"{number}. {text}")
    st.markdown("### Qué cubre")
    st.markdown("Adultos (18 años o más) con **hipertensión arterial, diabetes tipo 2, insuficiencia cardiaca, "
                "fibrilación auricular, enfermedad renal crónica o neumonía adquirida en la comunidad**, según guías "
                "de EsSalud-IETSI y el INS. Fuera de eso, el sistema responde *evidencia insuficiente*.")
    st.markdown("### Configuración actual")
    if dependencies.is_mock_mode():
        st.warning("**Modo simulado** (MOCK_MODE=1): respuestas de ejemplo, sin IA real. Sirve para probar la "
                   "interfaz sin gastar llamadas.", icon="🧪")
    else:
        models = dependencies.models_in_use()
        st.success("**IA real** · " + " · ".join(f"{ROLE_LABELS[r]}: `{m}`" for r, m in models.items()), icon="🤖")
