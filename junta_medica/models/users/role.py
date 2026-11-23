"""Role: el rol de una cuenta de usuario (RF15)."""
from enum import Enum


class Role(str, Enum):
    PHYSICIAN = "physician"   # médico tratante: registra casos y ve su propio historial
    ADMIN = "admin"           # administrador: además ve todo el historial y gestiona cuentas

    @property
    def can_manage_users(self) -> bool:
        return self is Role.ADMIN

    @property
    def can_see_all_history(self) -> bool:
        return self is Role.ADMIN
