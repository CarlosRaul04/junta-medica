"""
DDInterImporter: lee las descargas originales de DDInter (data/pharmacology/ddinter/*.csv) y se queda
solo con las interacciones entre medicamentos de NUESTRO catálogo.

DDInter: Xiong G. et al. Nucleic Acids Research 2022;50(D1):D1200-D1207. https://ddinter.scbdd.com/
Columnas de cada archivo: DDInterID_A, Drug_A, DDInterID_B, Drug_B, Level
"""
import csv
from itertools import product
from pathlib import Path

from junta_medica.models.pharmacology.interaction import Interaction
from junta_medica.models.pharmacology.severity import Severity
from junta_medica.repositories.pharmacology.drug_repository import DrugRepository

SOURCE = "DDInter"


class DDInterImporter:
    def __init__(self, drugs: DrugRepository, severity_map: dict[str, str]):
        self._severity_map = severity_map
        # nombre en inglés -> DCI(s). Un componente puede pertenecer a varias DCI
        # (ej. "Valsartan" -> valsartán y sacubitrilo/valsartán).
        self._inns_by_name: dict[str, set[str]] = {}
        for drug in drugs.all():
            for name in drug.english_names:
                self._inns_by_name.setdefault(name.lower(), set()).add(drug.inn)

    def load(self, files: list[Path]) -> list[Interaction]:
        """Si un par aparece varias veces (archivos o componentes distintos), se queda la severidad más alta."""
        by_pair: dict[frozenset[str], Interaction] = {}
        for row in self._rows(files):
            for interaction in self._parse_row(row):
                current = by_pair.get(interaction.pair)
                if current is None or interaction.severity.priority > current.severity.priority:
                    by_pair[interaction.pair] = interaction
        return sorted(by_pair.values(), key=lambda i: (i.drug_a, i.drug_b))

    def found_names(self, files: list[Path]) -> set[str]:
        """Nombres en inglés de nuestro catálogo que sí aparecen en DDInter (para el reporte de cobertura)."""
        found = set()
        for row in self._rows(files):
            for name in (row["Drug_A"], row["Drug_B"]):
                if name.strip().lower() in self._inns_by_name:
                    found.add(name.strip().lower())
        return found

    @staticmethod
    def _rows(files: list[Path]):
        for file in files:
            with open(file, encoding="utf-8", newline="") as content:
                yield from csv.DictReader(content)

    def _parse_row(self, row: dict) -> list[Interaction]:
        inns_a = self._inns_by_name.get(row["Drug_A"].strip().lower(), set())
        inns_b = self._inns_by_name.get(row["Drug_B"].strip().lower(), set())
        severity = Severity(self._severity_map.get(row["Level"].strip(), "unknown"))
        source_id = f"{row['DDInterID_A'].strip()}-{row['DDInterID_B'].strip()}"
        interactions = []
        for inn_a, inn_b in product(inns_a, inns_b):
            if inn_a != inn_b:
                first, second = sorted((inn_a, inn_b))
                interactions.append(Interaction(first, second, severity, SOURCE, source_id))
        return interactions
