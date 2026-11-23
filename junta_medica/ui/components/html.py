"""Ayudas para dibujar HTML seguro: todo texto que viene del usuario o de la IA se escapa."""
from html import escape

import streamlit as st


def esc(value) -> str:
    return escape(str(value if value is not None else ""))


def chip(text: str, tone: str = "") -> str:
    """Etiqueta redondeada. tone: teal | red | amber | green | gray | "" (borde)."""
    return f'<span class="jm-chip {tone}">{esc(text)}</span>'


def render(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)
