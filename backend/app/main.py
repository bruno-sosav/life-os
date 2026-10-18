from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analytics, auth, dashboard, finanzas, fisico, mental, negocio, rutina
from app.security import get_current_user

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


@app.middleware("http")
async def security_headers(request, call_next):  # type: ignore[no-untyped-def]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


# Pública: solo el login. Todo lo demás exige un token válido.
app.include_router(auth.router, prefix="/api")

protected = [Depends(get_current_user)]
for module in (rutina, dashboard, fisico, mental, negocio, finanzas, analytics):
    app.include_router(module.router, prefix="/api", dependencies=protected)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
