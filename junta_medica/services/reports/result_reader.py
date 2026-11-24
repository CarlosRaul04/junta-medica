"""
ResultReader: lee el resultado de un caso en formato diccionario (el JSON de DebateResultSerializer).

La pantalla de resultado, el informe PDF y el historial usan este lector, así una consulta guardada
se muestra igual que una recién calculada.
"""


class ResultReader:
    def __init__(self, data: dict):
        self.data = data

    # --- El caso ---
    @property
    def case_id(self) -> str:
        return self.data["case_id"]

    @property
    def case(self) -> dict:
        return self.data["evidence"]["case"]

    @property
    def drugs(self) -> list[dict]:
        return self.data["evidence"].get("drugs") or []

    @property
    def unrecognized_drugs(self) -> list[str]:
        return [d["original_name"] for d in self.drugs if not d.get("inn")]

    @property
    def guideline_chunks(self) -> list[dict]:
        return self.data["evidence"]["guidelines"].get("chunks") or []

    # --- El resultado ---
    @property
    def abstained(self) -> bool:
        return bool(self.data["abstained"])

    @property
    def abstention_reason(self) -> str:
        return self.data.get("abstention_reason", "")

    @property
    def verdict(self) -> dict | None:
        verdict = self.data.get("verdict")
        return verdict["output"] if verdict else None

    @property
    def insufficient_evidence(self) -> bool:
        """RF11: abstención sin debate o dictamen del Jefe que declara evidencia insuficiente."""
        return self.abstained or bool((self.verdict or {}).get("insufficient_evidence"))

    @property
    def primary_diagnosis(self) -> dict | None:
        return (self.verdict or {}).get("primary_diagnosis")

    @property
    def differential_diagnoses(self) -> list[dict]:
        return (self.verdict or {}).get("differential_diagnoses") or []

    @property
    def recommendations(self) -> list[dict]:
        return (self.verdict or {}).get("recommendations") or []

    @property
    def disagreements(self) -> list[str]:
        return list(self.data.get("unresolved_objections") or []) + list((self.verdict or {}).get("disagreements") or [])

    @property
    def limitations(self) -> list[str]:
        """Puntos concretos que las guías no cubren (el dictamen sigue siendo válido)."""
        return list((self.verdict or {}).get("limitations") or [])

    @property
    def alerts(self) -> list[dict]:
        return self.data.get("alerts") or []

    @property
    def highlighted_alerts(self) -> list[dict]:
        return [a for a in self.alerts if a.get("highlighted")]

    @property
    def other_alerts(self) -> list[dict]:
        return [a for a in self.alerts if not a.get("highlighted")]

    # --- El debate ---
    @property
    def rounds(self) -> list[dict]:
        return self.data.get("rounds") or []

    @property
    def last_proposal(self) -> dict | None:
        return self.rounds[-1]["proposal"]["output"] if self.rounds else None

    @property
    def turns(self) -> list[dict]:
        turns = [t for r in self.rounds for t in (r["proposal"], *r["reviews"])]
        return turns + ([self.data["verdict"]] if self.data.get("verdict") else [])

    # --- Métricas ---
    @property
    def summary(self) -> dict:
        return self.data.get("summary") or {}

    @property
    def citation_check(self) -> dict:
        return self.data.get("citation_check") or {}

    @property
    def traceability(self) -> float:
        return float(self.summary.get("traceability", 1.0))

    @property
    def agreement(self) -> float:
        return float(self.summary.get("final_agreement", 0.0))

    @property
    def seconds(self) -> float:
        return float(self.summary.get("seconds", self.data.get("seconds", 0.0)))

    @property
    def llm_calls(self) -> int:
        return int(self.summary.get("llm_calls", 0))

    @property
    def models(self) -> list[str]:
        return list(self.summary.get("models") or [])
