"""Errores propios del sistema. Todos en un solo lugar para encontrarlos fácil."""
from junta_medica.models.cases.validation_result import ValidationError


class InvalidCaseError(Exception):
    """El caso clínico no pasó la validación. Contiene la lista de problemas encontrados."""

    def __init__(self, errors: tuple[ValidationError, ...]):
        self.errors = errors
        super().__init__("; ".join(error.message for error in errors))


class LLMConfigurationError(Exception):
    """Falta configuración necesaria para usar la IA (por ejemplo, la clave de API)."""


class InvalidResponseError(Exception):
    """El modelo de lenguaje no devolvió un JSON válido."""


class OutdatedIndexError(Exception):
    """La base vectorial (chroma_db/) se creó con una versión anterior del código. Hay que reindexar."""

    def __init__(self):
        super().__init__("La base vectorial está desactualizada. Ejecuta: python -m scripts.index_guidelines")


class LLMProviderError(Exception):
    """El proveedor de IA respondió con un error (clave inválida, modelo inexistente, sin saldo, límite de uso)."""
