from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.app_config import get_settings
from app.core.conexion_database import SessionDep
from app.models import User

ALGORITHM = "HS256"

bearer = HTTPBearer(auto_error=False)

UNAUTHORIZED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Sesión inválida o vencida",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(user: User) -> tuple[str, datetime]:
    settings = get_settings()
    now = datetime.now(UTC)
    expires = now + timedelta(days=settings.access_token_days)
    claims = {"sub": user.id, "ver": user.token_version, "iat": now, "exp": expires}
    token = jwt.encode(claims, settings.jwt_secret.get_secret_value(), algorithm=ALGORITHM)
    return token, expires


def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise UNAUTHORIZED
    try:
        claims = jwt.decode(
            credentials.credentials,
            get_settings().jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "ver"]},
        )
    except jwt.PyJWTError:
        raise UNAUTHORIZED from None
    user = session.get(User, claims["sub"])
    if user is None or user.token_version != claims["ver"]:
        raise UNAUTHORIZED
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
