"""DrugRepository: el catálogo de medicamentos que el sistema reconoce (data/pharmacology/drugs.csv)."""
import csv
from pathlib import Path

from junta_medica.models.pharmacology.catalog_drug import CatalogDrug


class DrugRepository:
    def __init__(self, path: Path, separator: str, empty_value: str):
        self._separator = separator
        self._empty_value = empty_value
        self._by_inn: dict[str, CatalogDrug] = {}
        for drug in self._read(path):
            if drug.inn in self._by_inn:
                raise ValueError(f"DCI repetida en el catálogo: {drug.inn}")
            self._by_inn[drug.inn] = drug

    def all(self) -> list[CatalogDrug]:
        return list(self._by_inn.values())

    def find(self, inn: str) -> CatalogDrug | None:
        return self._by_inn.get(inn)

    def __len__(self) -> int:
        return len(self._by_inn)

    def _read(self, path: Path) -> list[CatalogDrug]:
        with open(path, encoding="utf-8", newline="") as file:
            return [self._parse_row(row) for row in csv.DictReader(file)]

    def _parse_row(self, row: dict) -> CatalogDrug:
        return CatalogDrug(
            inn=row["inn"].strip(),
            drug_class=row["drug_class"].strip(),
            atc=row["atc"].strip(),
            synonyms=self._split_list(row, "synonyms"),
            brands=self._split_list(row, "brands"),
            english_names=self._split_list(row, "english_names"),
            guidelines=self._split_list(row, "guidelines"),
        )

    def _split_list(self, row: dict, column: str) -> tuple[str, ...]:
        value = (row.get(column) or "").strip()
        if not value or value == self._empty_value:
            return ()
        return tuple(part.strip() for part in value.split(self._separator) if part.strip())
