"""IndexingSummary: cuántos fragmentos se indexaron por documento."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class IndexingSummary:
    chunks_by_document: dict[str, int] = field(default_factory=dict)

    @property
    def total_chunks(self) -> int:
        return sum(self.chunks_by_document.values())
