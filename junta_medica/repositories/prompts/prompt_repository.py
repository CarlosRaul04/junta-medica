"""PromptRepository: lee las instrucciones de cada agente desde data/prompts/<rol>.md."""
from pathlib import Path


class PromptRepository:
    def __init__(self, folder: Path):
        self._folder = folder
        self._cache: dict[str, str] = {}

    def get(self, role: str) -> str:
        if role not in self._cache:
            file = self._folder / f"{role}.md"
            if not file.exists():
                raise FileNotFoundError(f"No hay instrucciones para el agente '{role}': falta {file}")
            self._cache[role] = file.read_text(encoding="utf-8").strip()
        return self._cache[role]
