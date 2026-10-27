from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database.conexion_database import SessionDep
from app.core.seguridad.token_util import UNAUTHORIZED
from app.modules.auth import auth_service as service
from app.modules.auth.auth_model import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    """Dependencia que protege las rutas: exige un Bearer válido de un usuario vigente."""
    if credentials is None:
        raise UNAUTHORIZED
    return service.user_from_token(session, credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]
