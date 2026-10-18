from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.main import app
from app.models import User
from tests.conftest import PASSWORD, USERNAME


def login(client: TestClient, username: str = USERNAME, password: str = PASSWORD) -> int:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    status: int = response.status_code
    return status


def test_every_api_route_requires_auth(anon_client: TestClient) -> None:
    """Recorre TODAS las rutas /api del esquema: sin token, ninguna responde salvo el login."""
    public = {"/api/auth/login"}
    checked = 0
    for path, operations in app.openapi()["paths"].items():
        if not path.startswith("/api") or path in public:
            continue
        url = path.replace("{", "").replace("}", "")
        for method in operations:
            response = anon_client.request(method.upper(), url)
            assert response.status_code == 401, f"{method.upper()} {path} → {response.status_code}"
            checked += 1
    assert checked > 40


def test_login_and_me(anon_client: TestClient) -> None:
    response = anon_client.post(
        "/api/auth/login", json={"username": " Bruno ", "password": PASSWORD}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    me = anon_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json() == {"username": USERNAME}


def test_wrong_credentials_same_message(anon_client: TestClient) -> None:
    wrong_pass = anon_client.post(
        "/api/auth/login", json={"username": USERNAME, "password": "incorrecta"}
    )
    wrong_user = anon_client.post(
        "/api/auth/login", json={"username": "nadie", "password": PASSWORD}
    )
    assert wrong_pass.status_code == wrong_user.status_code == 401
    assert wrong_pass.json() == wrong_user.json()


def test_login_throttled_after_failures(anon_client: TestClient) -> None:
    for _ in range(5):
        assert login(anon_client, password="mal") == 401
    # bloqueado incluso con la contraseña correcta
    response = anon_client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0


@pytest.mark.parametrize(
    "token",
    [
        "no-es-un-jwt",
        jwt.encode(
            {"sub": "x", "ver": 0, "exp": datetime.now(UTC) + timedelta(days=1)},
            "otra-clave-distinta-de-32-caracteres!!",
        ),
    ],
)
def test_invalid_tokens_rejected(anon_client: TestClient, token: str) -> None:
    response = anon_client.get("/api/habits", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_expired_token_rejected(client: TestClient, db: sessionmaker[Session]) -> None:
    with db() as session:
        user = session.query(User).one()
        expired = jwt.encode(
            {"sub": user.id, "ver": 0, "exp": datetime.now(UTC) - timedelta(seconds=1)},
            get_settings().jwt_secret.get_secret_value(),
            algorithm="HS256",
        )
    response = client.get("/api/habits", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_password_change_revokes_tokens(client: TestClient, db: sessionmaker[Session]) -> None:
    assert client.get("/api/habits").status_code == 200
    with db() as session:
        session.query(User).one().token_version += 1
        session.commit()
    assert client.get("/api/habits").status_code == 401


def test_password_is_hashed(db: sessionmaker[Session]) -> None:
    with db() as session:
        stored = session.query(User).one().password_hash
    assert PASSWORD not in stored
    assert stored.startswith("$argon2id$")


def test_health_is_public_and_minimal(anon_client: TestClient) -> None:
    response = anon_client.get("/health")
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_docs_hidden_in_production() -> None:
    """En producción no hay /docs, /redoc ni /openapi.json (se evalúa al importar la app)."""
    import os
    import subprocess
    import sys

    script = (
        "from fastapi.testclient import TestClient\n"
        "from app.main import app\n"
        "c = TestClient(app)\n"
        "print([c.get(p).status_code for p in ('/docs', '/redoc', '/openapi.json', '/health')])\n"
    )
    env = {**os.environ, "ENVIRONMENT": "production"}
    result = subprocess.run(
        [sys.executable, "-c", script], env=env, capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "[404, 404, 404, 200]"


@pytest.mark.parametrize(
    ("origin", "allowed"),
    [
        ("http://localhost:5176", True),
        ("http://127.0.0.1:5173", True),
        ("https://evil.example", False),
        ("http://localhost.evil.example:5173", False),
    ],
)
def test_cors_in_development(anon_client: TestClient, origin: str, allowed: bool) -> None:
    response = anon_client.options(
        "/api/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert (response.status_code == 200) is allowed
