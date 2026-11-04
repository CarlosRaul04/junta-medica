"""ClinicalCase: los datos de un paciente ya validados. Incluye sus partes: Medication y Sexo."""
from dataclasses import dataclass, field
from enum import Enum


class Sex(str, Enum):
    FEMALE = "F"
    MALE = "M"


@dataclass(frozen=True)
class Medication:
    """Un medicamento que toma el paciente (tal como lo escribió el médico)."""
    name: str
    dose: str = ""


@dataclass(frozen=True)
class ClinicalCase:
    case_id: str
    age: int
    sex: Sex
    chief_complaint: str
    symptoms: tuple[str, ...]
    medications: tuple[Medication, ...]
    medical_history: tuple[str, ...] = ()
    allergies: tuple[str, ...] = ()
    lab_results: dict[str, float] = field(default_factory=dict)

    @property
    def medication_names(self) -> list[str]:
        return [drug.name for drug in self.medications]
