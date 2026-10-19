import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select

from app.config import get_settings
from app.db import SessionDep
from app.models import User

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()  # Argon2id

_DUMMY_HASH = password_hash.hash("dummy-password-for-timing")

bearer = HTTPBearer(auto_error=False)

UNAUTHORIZED = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Sesión inválida o vencida",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    return password_hash.verify(password, hashed or _DUMMY_HASH) and hashed is not None


def authenticate(session: SessionDep, username: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.username == username.strip().lower()))
    if not verify_password(password, user.password_hash if user else None):
        return None
    return user


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


class LoginThrottle:
    def __init__(self, max_failures: int = 5, window_seconds: int = 15 * 60) -> None:
        self.max_failures = max_failures
        self.window = window_seconds
        self._failures: defaultdict[str, deque[float]] = defaultdict(deque)

    def _recent(self, key: str) -> deque[float]:
        attempts = self._failures[key]
        while attempts and attempts[0] <= time.monotonic() - self.window:
            attempts.popleft()
        return attempts

    def check(self, request: Request) -> str:
        key = request.client.host if request.client else "unknown"
        attempts = self._recent(key)
        if len(attempts) >= self.max_failures:
            retry_after = int(attempts[0] + self.window - time.monotonic()) + 1
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Demasiados intentos fallidos. Probá más tarde.",
                headers={"Retry-After": str(retry_after)},
            )
        return key

    def fail(self, key: str) -> None:
        self._failures[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


login_throttle = LoginThrottle()
