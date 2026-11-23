"""
AuthService: crear cuentas, iniciar sesión y administrar roles (RF15).

La primera cuenta creada es de administrador; las siguientes, de médico tratante.
"""
import re

from junta_medica.exceptions import UserAccountError
from junta_medica.interfaces.user_store import UserStore
from junta_medica.models.users.role import Role
from junta_medica.models.users.user import User
from junta_medica.services.users.password_hasher import PasswordHasher


class AuthService:
    def __init__(self, users: UserStore, hasher: PasswordHasher, first_user_role: Role, default_role: Role,
                 username_pattern: str, username_rule: str, min_password_length: int):
        self._users = users
        self._hasher = hasher
        self._first_role = first_user_role
        self._default_role = default_role
        self._pattern = re.compile(username_pattern)
        self._username_rule = username_rule
        self._min_length = min_password_length

    def has_users(self) -> bool:
        return self._users.count() > 0

    def register(self, username: str, full_name: str, password: str, password_confirmation: str) -> User:
        username = username.strip().lower()
        full_name = " ".join(full_name.split())
        if not full_name:
            raise UserAccountError("Escribe tu nombre completo.")
        if not self._pattern.match(username):
            raise UserAccountError(f"El usuario debe tener {self._username_rule}.")
        if len(password) < self._min_length:
            raise UserAccountError(f"La contraseña debe tener al menos {self._min_length} caracteres.")
        if password != password_confirmation:
            raise UserAccountError("Las contraseñas no coinciden.")
        if self._users.find_with_hash(username):
            raise UserAccountError("Ese nombre de usuario ya existe. Elige otro.")
        role = self._first_role if not self.has_users() else self._default_role
        return self._users.add(username, full_name, self._hasher.hash(password), role)

    def login(self, username: str, password: str) -> User:
        found = self._users.find_with_hash(username.strip().lower())
        if not found or not self._hasher.verify(password, found[1]):
            raise UserAccountError("Usuario o contraseña incorrectos.")
        user = found[0]
        if not user.active:
            raise UserAccountError("Tu cuenta está desactivada. Consulta al administrador.")
        return user

    def all_users(self) -> list[User]:
        return self._users.all()

    def change_role(self, acting_user: User, user_id: int, role: Role) -> None:
        self._check_admin_change(acting_user, user_id)
        self._users.update_role(user_id, role)

    def set_active(self, acting_user: User, user_id: int, active: bool) -> None:
        self._check_admin_change(acting_user, user_id)
        self._users.set_active(user_id, active)

    @staticmethod
    def _check_admin_change(acting_user: User, user_id: int) -> None:
        if not acting_user.role.can_manage_users:
            raise UserAccountError("Solo el administrador puede cambiar cuentas.")
        if acting_user.user_id == user_id:
            raise UserAccountError("No puedes cambiar tu propia cuenta (así nunca te quedas sin administrador).")
