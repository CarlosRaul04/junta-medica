"""
ProgressTracker: muestra en vivo lo que hace la junta mientras trabaja (implementa DebateObserver).

Cada agente aparece "trabajando…" y, al terminar, se reemplaza por un resumen de lo que dijo.
"""
import streamlit as st

from junta_medica.config.texts import ROLE_LABELS, STANCE_LABELS
from junta_medica.interfaces.debate_observer import DebateObserver

_WORKING = {
    "clinical": "analiza el caso y propone diagnósticos y plan",
    "pharmacological": "revisa la medicación, interacciones y dosis",
    "protocol": "contrasta la propuesta con las guías de práctica clínica",
    "chief": "integra el debate y redacta la segunda opinión",
}


def _count(number: int, singular: str, plural: str) -> str:
    return f"{number} {singular if number == 1 else plural}"


class ProgressTracker(DebateObserver):
    def __init__(self, max_rounds: int):
        self._max_rounds = max_rounds
        self._panel = st.container(border=True)
        with self._panel:
            self._title = st.empty()
            self._bar = st.empty()
        self._set_title("⏳ Revisando la medicación y buscando en las guías…")
        self._done_steps = 0
        self._total_steps = 2 + 3 * max_rounds        # herramientas + 3 agentes por ronda + jefe
        self._bar.progress(0.03)
        self._current = None

    def evidence_collected(self, evidence) -> None:
        recognized = sum(1 for d in evidence.drugs if d.recognized)
        sufficient = "suficiente" if evidence.guidelines.sufficient_evidence else "**insuficiente**"
        self._write(f"✅ **Herramientas sin IA** · {recognized} de {len(evidence.drugs)} medicamentos reconocidos · "
                    f"{_count(len(evidence.interactions), 'interacción', 'interacciones')} · "
                    f"{_count(len(evidence.conditions.findings), 'alerta', 'alertas')} por condición del paciente · "
                    f"{_count(len(evidence.guidelines.chunks), 'fragmento', 'fragmentos')} de guías "
                    f"(evidencia {sufficient})")
        self._advance()

    def agent_started(self, role: str, round_number: int) -> None:
        label = ROLE_LABELS.get(role, role)
        prefix = f"Ronda {round_number} · " if round_number else ""
        with self._panel:
            self._current = st.empty()
        self._current.markdown(f"⏳ {prefix}**{label}** {_WORKING.get(role, 'trabaja')}…")
        self._set_title(f"⏳ {prefix}{label} trabajando…")

    def agent_finished(self, turn) -> None:
        label = ROLE_LABELS.get(turn.role, turn.role)
        prefix = f"Ronda {turn.round_number} · " if turn.round_number else ""
        self._current.markdown(f"✅ {prefix}**{label}** · {self._summary(turn)} · _{turn.llm.seconds:.0f} s_")
        self._advance()

    def round_finished(self, debate_round) -> None:
        level = f"acuerdo {debate_round.agreement_level:.0%}"
        if debate_round.consensus:
            self._write(f"🤝 **Ronda {debate_round.number}: consenso** ({level}). Pasa al Médico Jefe.")
            self._done_steps = self._total_steps - 1
        elif debate_round.number < self._max_rounds:
            self._write(f"🔁 **Ronda {debate_round.number}: sin consenso** ({level}). "
                        "El Agente Clínico corrige su propuesta con las objeciones.")
        else:
            self._write(f"⚠️ **Ronda {debate_round.number}: sin consenso** tras el máximo de rondas. "
                        "El Médico Jefe registrará las discrepancias.")
            self._done_steps = self._total_steps - 1

    def abstained(self, reason: str) -> None:
        self._write("⛔ **Evidencia insuficiente:** las guías no cubren este caso. La junta no debate "
                    "(no se gastan llamadas a la IA).")

    def finish(self, insufficient: bool) -> None:
        self._bar.progress(1.0)
        self._set_title("✅ Terminado: evidencia insuficiente" if insufficient else "✅ La junta terminó su dictamen")

    def fail(self, message: str) -> None:
        self._set_title(f"❌ {message}")

    # ------------------------------------------------------------------
    def _set_title(self, text: str) -> None:
        self._title.markdown(f"#### {text}")

    def _write(self, text: str) -> None:
        with self._panel:
            st.markdown(text)

    def _advance(self) -> None:
        self._done_steps += 1
        self._bar.progress(min(self._done_steps / self._total_steps, 0.97))

    @staticmethod
    def _summary(turn) -> str:
        output = turn.output
        if turn.role == "clinical":
            return "propone " + ", ".join(f"{d.icd10} {d.name}" for d in output.diagnoses[:3])
        if turn.role == "chief":
            primary = output.primary_diagnosis
            return f"dictamen listo: {primary.icd10} {primary.name}" if primary else "dictamen listo"
        stance = STANCE_LABELS.get(output.stance.value, output.stance.value)
        severe = sum(1 for o in output.objections if o.severity.value == "severe")
        return stance + (f" ({severe} objeción grave)" if severe == 1 else f" ({severe} objeciones graves)" if severe else "")
