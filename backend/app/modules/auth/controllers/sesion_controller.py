from fastapi import APIRouter, Request

from app.core.database.conexion_database import SessionDep
from app.modules.auth.schemas.sesion_schema import LoginIn, TokenOut
from app.modules.auth.services import sesion_service

router = APIRouter()


def _client_ip(request: Request) -> str:
    """IP real del cliente. El proxy de Railway la agrega al final de X-Forwarded-For;
    las anteriores las puede inventar el cliente para saltear el límite de intentos."""
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[-1].strip()
    return forwarded or (request.client.host if request.client else "unknown")


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, session: SessionDep) -> TokenOut:
    token, expires = sesion_service.login(
        session, payload.username, payload.password, _client_ip(request)
    )
    return TokenOut(access_token=token, expires_at=expires)
