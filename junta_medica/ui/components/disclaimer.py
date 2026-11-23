"""Aviso legal al pie de las pantallas con resultados (RF17)."""
from junta_medica.config.texts import DISCLAIMER
from junta_medica.ui.components.html import esc, render


def disclaimer() -> None:
    render(f'<div class="jm-disclaimer">⚕️ {esc(DISCLAIMER)}</div>')
