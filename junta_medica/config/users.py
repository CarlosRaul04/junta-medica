"""Cuentas de usuario y roles (RF15, RNF04)."""
from junta_medica.models.users.role import Role

ROLE_LABELS = {Role.PHYSICIAN: "Médico tratante", Role.ADMIN: "Administrador"}
FIRST_USER_ROLE = Role.ADMIN        # la primera cuenta que se crea administra el sistema
DEFAULT_ROLE = Role.PHYSICIAN       # las siguientes son de médico (el administrador puede cambiarlas)

USERNAME_PATTERN = r"^[a-z0-9._]{3,30}$"
USERNAME_RULE = "de 3 a 30 caracteres: letras minúsculas, números, punto o guion bajo"
MIN_PASSWORD_LENGTH = 8
