"""
LabelInteractionRepository: interacciones tomadas a mano de fichas técnicas (data/pharmacology/label_interactions.csv).

Sirve para medicamentos que DDInter no cubre (dabigatrán, finerenona, gliclazida).
Columnas: drug_a, drug_b, severity, source (id del catálogo de documentos), page, note.
La cita queda como "<source>:p<page>" (ej. "ft_dabigatran:p84").
"""
import csv
from pathlib import Path

from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity


class LabelInteractionRepository:
    def __init__(self, path: Path):
        self._path = path

    def read_all(self) -> list[Interaction]:
        with open(self._path, encoding="utf-8", newline="") as file:
            interactions = []
            for row in csv.DictReader(file):
                first, second = sorted((row["drug_a"].strip(), row["drug_b"].strip()))
                interactions.append(Interaction(first, second, Severity(row["severity"].strip()),
                                                row["source"].strip(), f"p{int(row['page'])}"))
            return interactions
