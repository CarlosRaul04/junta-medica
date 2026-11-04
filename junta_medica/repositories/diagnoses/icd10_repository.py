"""Icd10Repository: la tabla de códigos CIE-10 (data/references/icd10.csv), generada desde el PDF de la OPS."""
import csv
from pathlib import Path

from junta_medica.models.diagnoses.icd10_code import Icd10Code

COLUMNS = ["code", "title", "page"]


class Icd10Repository:
    def __init__(self, path: Path):
        self._path = path
        self._by_code: dict[str, Icd10Code] | None = None

    def all(self) -> list[Icd10Code]:
        return list(self._index().values())

    def find(self, code: str) -> Icd10Code | None:
        """Acepta "I500", "i50.0" o "I50.0"."""
        return self._index().get(self.normalize(code))

    def __len__(self) -> int:
        return len(self._index())

    def save_all(self, codes: list[Icd10Code]) -> None:
        with open(self._path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
            for c in codes:
                writer.writerow({"code": c.code, "title": c.title, "page": c.page})
        self._by_code = None

    @staticmethod
    def normalize(code: str) -> str:
        cleaned = code.strip().upper().replace(" ", "").rstrip("*†")
        if len(cleaned) == 4 and "." not in cleaned:
            cleaned = f"{cleaned[:3]}.{cleaned[3]}"
        return cleaned

    def _index(self) -> dict[str, Icd10Code]:
        if self._by_code is None:
            with open(self._path, encoding="utf-8", newline="") as file:
                self._by_code = {
                    row["code"]: Icd10Code(row["code"], row["title"], int(row["page"]))
                    for row in csv.DictReader(file)
                }
        return self._by_code
