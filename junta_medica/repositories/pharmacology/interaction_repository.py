"""InteractionRepository: guarda y lee la tabla de interacciones (data/pharmacology/interactions.csv)."""
import csv
from pathlib import Path

from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity

COLUMNS = ["drug_a", "drug_b", "severity", "source", "source_id"]


class InteractionRepository:
    def __init__(self, path: Path):
        self._path = path

    def read_all(self) -> list[Interaction]:
        with open(self._path, encoding="utf-8", newline="") as file:
            return [
                Interaction(f["drug_a"], f["drug_b"], Severity(f["severity"]), f["source"], f["source_id"])
                for f in csv.DictReader(file)
            ]

    def save_all(self, interactions: list[Interaction]) -> None:
        with open(self._path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            for i in interactions:
                writer.writerow({
                    "drug_a": i.drug_a, "drug_b": i.drug_b,
                    "severity": i.severity.value, "source": i.source, "source_id": i.source_id,
                })
