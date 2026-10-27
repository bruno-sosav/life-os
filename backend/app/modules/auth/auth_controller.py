from fastapi import APIRouter, Request

from app.core.database.conexion_database import SessionDep
from app.modules.auth import auth_service as service
from app.modules.auth.auth_dependency import CurrentUser
from app.modules.auth.auth_schema import LoginIn, MeOut, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str:
    """IP real del cliente. El proxy de Railway la agrega al final de X-Forwarded-For;
    las anteriores las puede inventar el cliente para saltear el límite de intentos."""
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[-1].strip()
    return forwarded or (request.client.host if request.client else "unknown")


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, session: SessionDep) -> TokenOut:
    token, expires = service.login(session, payload.username, payload.password, _client_ip(request))
    return TokenOut(access_token=token, expires_at=expires)


@router.get("/me", response_model=MeOut)
def me(user: CurrentUser) -> MeOut:
    return MeOut(username=user.username)
