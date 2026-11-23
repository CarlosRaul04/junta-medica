import pytest

from junta_medica.exceptions import UserAccountError
from junta_medica.models.users.role import Role


def test_first_account_is_admin_and_next_are_physicians(auth):
    admin = auth.register("Admin", " Ana  Pérez ", "clave-segura", "clave-segura")
    doctor = auth.register("drlopez", "Luis López", "otra-clave", "otra-clave")
    assert admin.username == "admin" and admin.full_name == "Ana Pérez" and admin.role is Role.ADMIN
    assert doctor.role is Role.PHYSICIAN


def test_login_checks_password_and_active_account(auth):
    admin = auth.register("admin", "Ana", "clave-segura", "clave-segura")
    doctor = auth.register("drlopez", "Luis", "otra-clave", "otra-clave")
    assert auth.login(" DRLOPEZ ", "otra-clave").user_id == doctor.user_id
    with pytest.raises(UserAccountError, match="incorrectos"):
        auth.login("drlopez", "mala-clave")
    auth.set_active(admin, doctor.user_id, False)
    with pytest.raises(UserAccountError, match="desactivada"):
        auth.login("drlopez", "otra-clave")


@pytest.mark.parametrize("username, password, confirmation, message", [
    ("ab", "clave-segura", "clave-segura", "3 a 30"),
    ("con espacio", "clave-segura", "clave-segura", "3 a 30"),
    ("valido", "corta", "corta", "al menos 8"),
    ("valido", "clave-segura", "otra-cosa", "no coinciden"),
])
def test_register_rejects_invalid_data(auth, username, password, confirmation, message):
    with pytest.raises(UserAccountError, match=message):
        auth.register(username, "Nombre", password, confirmation)


def test_duplicate_username_is_rejected(auth):
    auth.register("admin", "Ana", "clave-segura", "clave-segura")
    with pytest.raises(UserAccountError, match="ya existe"):
        auth.register("admin", "Otra", "clave-segura", "clave-segura")


def test_only_admin_changes_accounts_and_never_its_own(auth):
    admin = auth.register("admin", "Ana", "clave-segura", "clave-segura")
    doctor = auth.register("drlopez", "Luis", "otra-clave", "otra-clave")
    with pytest.raises(UserAccountError, match="Solo el administrador"):
        auth.change_role(doctor, admin.user_id, Role.PHYSICIAN)
    with pytest.raises(UserAccountError, match="propia cuenta"):
        auth.change_role(admin, admin.user_id, Role.PHYSICIAN)
    auth.change_role(admin, doctor.user_id, Role.ADMIN)
    assert {u.username: u.role for u in auth.all_users()}["drlopez"] is Role.ADMIN


def test_passwords_are_not_stored_in_plain_text(auth, database):
    auth.register("admin", "Ana", "clave-segura", "clave-segura")
    with database.connect() as db:
        stored = db.execute("SELECT password_hash FROM users").fetchone()[0]
    assert "clave-segura" not in stored and stored.startswith("$2")
