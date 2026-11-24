"""MongoUserStore: las cuentas de usuario en MongoDB (colección users)."""
from datetime import datetime, timezone

from junta_medica.interfaces.user_store import UserStore
from junta_medica.models.users.role import Role
from junta_medica.models.users.user import User
from junta_medica.repositories.database.mongo_database import MongoDatabase


class MongoUserStore(UserStore):
    def __init__(self, database: MongoDatabase):
        self._database = database

    def count(self) -> int:
        return self._database.users.count_documents({})

    def add(self, username: str, full_name: str, password_hash: str, role: Role) -> User:
        user_id = self._database.next_id("users")
        self._database.users.insert_one({
            "user_id": user_id, "username": username, "full_name": full_name, "password_hash": password_hash,
            "role": role.value, "active": True, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        return User(user_id, username, full_name, role)

    def find_with_hash(self, username: str) -> tuple[User, str] | None:
        document = self._database.users.find_one({"username": username})
        return (self._to_user(document), document["password_hash"]) if document else None

    def all(self) -> list[User]:
        return [self._to_user(d) for d in self._database.users.find().sort("user_id", 1)]

    def update_role(self, user_id: int, role: Role) -> None:
        self._database.users.update_one({"user_id": user_id}, {"$set": {"role": role.value}})

    def set_active(self, user_id: int, active: bool) -> None:
        self._database.users.update_one({"user_id": user_id}, {"$set": {"active": active}})

    @staticmethod
    def _to_user(document: dict) -> User:
        return User(document["user_id"], document["username"], document["full_name"], Role(document["role"]),
                    bool(document["active"]))
