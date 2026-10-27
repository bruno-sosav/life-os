from fastapi import APIRouter, Request

from app.core.database.conexion_database import SessionDep
from app.modules.auth import auth_service as service
from app.modules.auth.auth_dependency import CurrentUser
from app.modules.auth.auth_schema import LoginIn, MeOut, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, session: SessionDep) -> TokenOut:
    client_ip = request.client.host if request.client else "unknown"
    token, expires = service.login(session, payload.username, payload.password, client_ip)
    return TokenOut(access_token=token, expires_at=expires)


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser) -> MeOut:
    return MeOut(username=user.username)
