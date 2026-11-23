"""User: una cuenta de usuario del sistema (sin la contraseña)."""
from dataclasses import dataclass

from junta_medica.models.users.role import Role


@dataclass(frozen=True)
class User:
    user_id: int
    username: str
    full_name: str
    role: Role
    active: bool = True
