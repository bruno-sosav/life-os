import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.modules.auth import auth_service as service
from app.modules.auth.auth_model import User
from tests.conftest import PASSWORD, USERNAME

NEW_PASSWORD = "otra-clave-bien-larga"


def test_create_user_normalizes_and_hashes(db: sessionmaker[Session]) -> None:
    with db() as session:
        user = service.create_user(session, "  Ana  ", NEW_PASSWORD)
        assert user.username == "ana"
        assert user.password_hash.startswith("$argon2id$")
        assert service.authenticate(session, "ANA", NEW_PASSWORD) is not None


@pytest.mark.parametrize(
    ("username", "password", "error"),
    [
        (USERNAME, NEW_PASSWORD, "ya existe"),
        ("   ", NEW_PASSWORD, "inválido"),
        ("x" * 51, NEW_PASSWORD, "inválido"),
        ("ana", "corta", "al menos 12"),
    ],
)
def test_create_user_rejects(
    db: sessionmaker[Session], username: str, password: str, error: str
) -> None:
    with db() as session, pytest.raises(ValueError, match=error):
        service.create_user(session, username, password)


def test_set_password_revokes_sessions(db: sessionmaker[Session]) -> None:
    with db() as session:
        token_version = session.query(User).one().token_version
        user = service.set_password(session, USERNAME, NEW_PASSWORD)
        assert user.token_version == token_version + 1
        assert service.authenticate(session, USERNAME, PASSWORD) is None
        assert service.authenticate(session, USERNAME, NEW_PASSWORD) is not None


def test_set_password_unknown_user(db: sessionmaker[Session]) -> None:
    with db() as session, pytest.raises(ValueError, match="no existe"):
        service.set_password(session, "nadie", NEW_PASSWORD)
