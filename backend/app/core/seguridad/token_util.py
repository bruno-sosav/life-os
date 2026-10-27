from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.core.app_config import get_settings

ALGORITHM = "HS256"

UNAUTHORIZED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Sesión inválida o vencida",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_token(subject: str, version: int) -> tuple[str, datetime]:
    """JWT firmado. `version` permite invalidar todos los tokens de un usuario de una vez."""
    settings = get_settings()
    now = datetime.now(UTC)
    expires = now + timedelta(days=settings.access_token_days)
    claims = {"sub": subject, "ver": version, "iat": now, "exp": expires}
    token = jwt.encode(claims, settings.jwt_secret.get_secret_value(), algorithm=ALGORITHM)
    return token, expires


def read_token(token: str) -> tuple[str, int]:
    """Devuelve (sub, ver) si la firma y el vencimiento son válidos; si no, 401."""
    try:
        claims = jwt.decode(
            token,
            get_settings().jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "ver"]},
        )
    except jwt.PyJWTError:
        raise UNAUTHORIZED from None
    return claims["sub"], claims["ver"]
