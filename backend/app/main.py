from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.app_config import get_settings
from app.core.seguridad.seguridad_middleware import security_headers
from app.core.seguridad.sesion_dependency import get_current_user
from app.modules import finanzas, mental
from app.routers import analytics, auth, dashboard, fisico, negocio, rutina

settings = get_settings()

# En producción no se publica la documentación ni el esquema de la API.
docs_enabled = not settings.is_production
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug and docs_enabled,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # En desarrollo, Vite puede arrancar en cualquier puerto libre de localhost
    allow_origin_regex=None if settings.is_production else r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.middleware("http")(security_headers)

app.include_router(auth.router, prefix="/api")

protected = [Depends(get_current_user)]
for module in (rutina, dashboard, fisico, mental, negocio, finanzas, analytics):
    app.include_router(module.router, prefix="/api", dependencies=protected)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
