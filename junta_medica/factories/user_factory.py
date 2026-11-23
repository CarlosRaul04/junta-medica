"""Arma el servicio de cuentas de usuario (config/users.py)."""
from junta_medica.config import users as config
from junta_medica.factories.storage_factory import create_user_store
from junta_medica.interfaces.user_store import UserStore
from junta_medica.services.users.auth_service import AuthService
from junta_medica.services.users.password_hasher import PasswordHasher


def create_auth_service(store: UserStore | None = None) -> AuthService:
    return AuthService(store or create_user_store(), PasswordHasher(), config.FIRST_USER_ROLE, config.DEFAULT_ROLE,
                       config.USERNAME_PATTERN, config.USERNAME_RULE, config.MIN_PASSWORD_LENGTH)
