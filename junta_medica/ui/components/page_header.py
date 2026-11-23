"""Encabezado de cada pantalla: etiqueta pequeña, título y una línea que explica qué se hace aquí."""
from junta_medica.ui.components.html import esc, render


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    sub = f'<div class="jm-subtitle">{esc(subtitle)}</div>' if subtitle else ""
    render(f'<div class="jm-header"><div class="jm-eyebrow">{esc(eyebrow)}</div>'
           f'<div class="jm-title">{esc(title)}</div>{sub}</div>')
