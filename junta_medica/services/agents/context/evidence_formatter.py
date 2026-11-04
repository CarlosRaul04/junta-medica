"""EvidenceFormatter: fragmentos de guía y hallazgos farmacológicos como texto, cada uno con su cita entre corchetes."""
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk
from junta_medica.models.pharmacology.condition_finding import ConditionCheckResult
from junta_medica.models.pharmacology.interaction_finding import InteractionFinding
from junta_medica.models.pharmacology.normalized_drug import NormalizedDrug
from junta_medica.services.agents.context.observation_text import readable_observation


class EvidenceFormatter:
    def __init__(self, severity_labels: dict[str, str], fragment_max_chars: int, lab_labels: dict[str, str]):
        self._severity = severity_labels
        self._max_chars = fragment_max_chars
        self._labs = lab_labels

    def fragments(self, chunks: tuple[RetrievedChunk, ...] | list[RetrievedChunk]) -> str:
        if not chunks:
            return "No se encontraron fragmentos de guía relacionados."
        blocks = []
        for retrieved in chunks:
            chunk = retrieved.chunk
            text = " ".join(chunk.text.split())
            if len(text) > self._max_chars:
                text = text[: self._max_chars].rsplit(" ", 1)[0] + " [...]"
            blocks.append(f"[{chunk.citation}] {text}")
        return "\n\n".join(blocks)

    @staticmethod
    def drugs(drugs: tuple[NormalizedDrug, ...]) -> str:
        lines = []
        for drug in drugs:
            if not drug.recognized:
                lines.append(f"- {drug.original_name}: NO RECONOCIDO (no está en el catálogo; no se pudo revisar)")
            elif drug.needs_confirmation:
                lines.append(f"- {drug.original_name} -> {drug.inn} (nombre aproximado: confirmar)")
            elif drug.original_name.strip().lower() != drug.inn:
                lines.append(f"- {drug.original_name} -> {drug.inn}")
            else:
                lines.append(f"- {drug.inn}")
        return "\n".join(lines) if lines else "- ninguno"

    def interactions(self, findings: tuple[InteractionFinding, ...]) -> str:
        if not findings:
            return "- Ninguna interacción grave o moderada en la tabla."
        lines = []
        for finding in findings:
            i = finding.interaction
            lines.append(f"- [{i.citation}] {i.drug_a} + {i.drug_b}: interacción {self._severity[i.severity.value].upper()}")
        return "\n".join(lines)

    def conditions(self, result: ConditionCheckResult) -> str:
        lines = []
        for finding in result.findings:
            rule = finding.rule
            lines.append(f"- [{rule.citation}] {rule.drug} ({readable_observation(finding.observed_value, self._labs)}) — {self._severity[rule.severity.value].upper()}: "
                         f"{rule.effect} Recomendación: {rule.recommendation}")
        for rule in result.not_evaluable:
            lines.append(f"- Sin dato para evaluar: {rule.drug} requiere «{self._labs.get(rule.parameter, rule.parameter)}» ({rule.effect})")
        return "\n".join(lines) if lines else "- Ninguna regla fármaco–condición se cumple."
