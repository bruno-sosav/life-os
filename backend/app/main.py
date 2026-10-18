from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analytics, dashboard, finanzas, fisico, mental, negocio, rutina

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rutina.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(fisico.router, prefix="/api")
app.include_router(mental.router, prefix="/api")
app.include_router(negocio.router, prefix="/api")
app.include_router(finanzas.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
