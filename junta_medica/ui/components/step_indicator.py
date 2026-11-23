"""Indicador de pasos del formulario: los pasos hechos en verde, el actual resaltado."""
from junta_medica.ui.components.html import esc, render


def step_indicator(steps: list[str], current: int) -> None:
    items = []
    for index, name in enumerate(steps):
        state = "done" if index < current else "current" if index == current else ""
        items.append(f'<div class="jm-step {state}"><b>Paso {index + 1}</b>{esc(name)}</div>')
    render(f'<div class="jm-steps">{"".join(items)}</div>')
