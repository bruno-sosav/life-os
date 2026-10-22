from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.core.conexion_database import SessionDep
from app.core.contrasena_util import verify_password
from app.core.limite_intentos_util import login_throttle
from app.core.sesion_dependency import CurrentUser, create_access_token
from app.models import User
from app.schemas.auth import LoginIn, MeOut, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate(session: SessionDep, username: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.username == username.strip().lower()))
    if not verify_password(password, user.password_hash if user else None):
        return None
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, session: SessionDep) -> TokenOut:
    key = login_throttle.check(request)
    user = authenticate(session, payload.username, payload.password)
    if user is None:
        login_throttle.fail(key)
        # Mismo mensaje para usuario inexistente y contraseña incorrecta
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos")
    login_throttle.reset(key)
    token, expires = create_access_token(user)
    return TokenOut(access_token=token, expires_at=expires)


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser) -> MeOut:
    return MeOut(username=user.username)
