from fastapi import APIRouter, HTTPException, Request, status

from app.db import SessionDep
from app.schemas.auth import LoginIn, MeOut, TokenOut
from app.security import CurrentUser, authenticate, create_access_token, login_throttle

router = APIRouter(prefix="/auth", tags=["auth"])


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
