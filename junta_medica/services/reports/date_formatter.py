"""DateFormatter: muestra las fechas guardadas en UTC en la hora local del usuario (Perú)."""
from datetime import datetime
from zoneinfo import ZoneInfo


class DateFormatter:
    def __init__(self, timezone: str):
        self._zone = ZoneInfo(timezone)

    def format(self, iso_utc: str) -> str:
        """"2026-11-23T22:43:00+00:00" -> "23/11/2026 17:43"."""
        try:
            return datetime.fromisoformat(iso_utc).astimezone(self._zone).strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return iso_utc
