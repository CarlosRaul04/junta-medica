"""CaseLoader: valida los datos y, si son correctos, los convierte en ClinicalCase."""
from pathlib import Path

from junta_medica.exceptions import InvalidCaseError
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.repositories.cases.case_repository import CaseRepository
from junta_medica.services.cases.case_converter import CaseConverter
from junta_medica.services.cases.case_validator import CaseValidator


class CaseLoader:
    def __init__(self, validator: CaseValidator, converter: CaseConverter, repository: CaseRepository):
        self._validator = validator
        self._converter = converter
        self._repository = repository

    def from_dict(self, data: dict) -> ClinicalCase:
        """Para datos que vienen del formulario."""
        result = self._validator.validate(data)
        if not result.is_valid:
            raise InvalidCaseError(result.errors)
        return self._converter.convert(data)

    def from_file(self, path: Path) -> ClinicalCase:
        """Para los casos simulados en data/cases/ (solo usa la sección 'caso')."""
        return self.from_dict(self._repository.read_clinical_data(path))
