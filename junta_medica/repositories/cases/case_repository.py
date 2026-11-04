"""CaseRepository: lee los archivos JSON de casos (data/cases/CASO-XXX.json)."""
import json
from pathlib import Path

from junta_medica.exceptions import InvalidCaseError
from junta_medica.models.cases.validation_result import ValidationError

CASE_SECTION = "case"          # datos clínicos (lo único que ven los agentes)
EXPECTED_SECTION = "expected"  # respuesta correcta (solo para la evaluación)


class CaseRepository:
    def __init__(self, folder: Path):
        self._folder = folder

    def list_files(self) -> list[Path]:
        return sorted(self._folder.glob("CASO-*.json"))

    def read_clinical_data(self, path: Path) -> dict:
        """Devuelve solo la sección 'caso' (sin validar todavía)."""
        content = self._read_json(path)
        if CASE_SECTION not in content:
            raise InvalidCaseError((ValidationError("file", f"El archivo no tiene la sección '{CASE_SECTION}'."),))
        return content[CASE_SECTION]

    def read_expected(self, path: Path) -> dict:
        """Devuelve la sección 'esperado' (solo la usa la evaluación; nunca los agentes)."""
        return self._read_json(path).get(EXPECTED_SECTION, {})

    @staticmethod
    def _read_json(path: Path) -> dict:
        try:
            content = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise InvalidCaseError((ValidationError("file", f"El archivo {Path(path).name} no es un JSON válido."),))
        if not isinstance(content, dict):
            raise InvalidCaseError((ValidationError("file", "El archivo debe contener un objeto JSON."),))
        return content
