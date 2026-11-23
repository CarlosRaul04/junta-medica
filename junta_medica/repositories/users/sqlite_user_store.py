"""SQLiteUserStore: las cuentas de usuario en SQLite."""
from datetime import datetime, timezone

from junta_medica.interfaces.user_store import UserStore
from junta_medica.models.users.role import Role
from junta_medica.models.users.user import User
from junta_medica.repositories.database.sqlite_database import SQLiteDatabase


class SQLiteUserStore(UserStore):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def count(self) -> int:
        with self._database.connect() as db:
            return db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def add(self, username: str, full_name: str, password_hash: str, role: Role) -> User:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._database.connect() as db:
            cursor = db.execute(
                "INSERT INTO users (username, full_name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (username, full_name, password_hash, role.value, created_at),
            )
            return User(cursor.lastrowid, username, full_name, role)

    def find_with_hash(self, username: str) -> tuple[User, str] | None:
        with self._database.connect() as db:
            row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return (self._to_user(row), row["password_hash"]) if row else None

    def all(self) -> list[User]:
        with self._database.connect() as db:
            return [self._to_user(row) for row in db.execute("SELECT * FROM users ORDER BY user_id")]

    def update_role(self, user_id: int, role: Role) -> None:
        with self._database.connect() as db:
            db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role.value, user_id))

    def set_active(self, user_id: int, active: bool) -> None:
        with self._database.connect() as db:
            db.execute("UPDATE users SET active = ? WHERE user_id = ?", (int(active), user_id))

    @staticmethod
    def _to_user(row) -> User:
        return User(row["user_id"], row["username"], row["full_name"], Role(row["role"]), bool(row["active"]))
