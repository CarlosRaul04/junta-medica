"""UserStore: guarda y lee cuentas de usuario (implementaciones: SQLite local; luego PostgreSQL en AWS RDS)."""
from abc import ABC, abstractmethod

from junta_medica.models.users.role import Role
from junta_medica.models.users.user import User


class UserStore(ABC):
    @abstractmethod
    def count(self) -> int:
        ...

    @abstractmethod
    def add(self, username: str, full_name: str, password_hash: str, role: Role) -> User:
        ...

    @abstractmethod
    def find_with_hash(self, username: str) -> tuple[User, str] | None:
        """El usuario y el hash de su contraseña (solo para verificarla al iniciar sesión)."""

    @abstractmethod
    def all(self) -> list[User]:
        ...

    @abstractmethod
    def update_role(self, user_id: int, role: Role) -> None:
        ...

    @abstractmethod
    def set_active(self, user_id: int, active: bool) -> None:
        ...
