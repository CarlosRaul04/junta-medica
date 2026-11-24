"""
MongoDatabase: la base MongoDB (colecciones users, consultations y counters) y sus índices.

Los ids son números enteros consecutivos (1, 2, 3...) como en SQLite: los genera la colección
`counters`, así el resto del sistema no cambia (Consultation N.° 1, CASO del historial...).
"""
from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.database import Database


class MongoDatabase:
    def __init__(self, client, database_name: str):
        self._db: Database = client[database_name]
        self.users.create_index([("username", ASCENDING)], unique=True)
        self.users.create_index([("user_id", ASCENDING)], unique=True)
        self.consultations.create_index([("consultation_id", DESCENDING)], unique=True)
        self.consultations.create_index([("user_id", ASCENDING)])

    @property
    def users(self):
        return self._db["users"]

    @property
    def consultations(self):
        return self._db["consultations"]

    def next_id(self, sequence: str) -> int:
        """Siguiente número de la secuencia (ej. "users" -> 1, 2, 3...), seguro aunque haya varios usuarios a la vez."""
        counter = self._db["counters"].find_one_and_update(
            {"_id": sequence}, {"$inc": {"value": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
        return counter["value"]
