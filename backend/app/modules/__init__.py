"""Importar los módulos registra todas sus tablas en Base.metadata (lo usan Alembic y los tests)."""

from app.modules import analytics, auth, dashboard, finanzas, fisico, mental, negocio, rutina

__all__ = ["analytics", "auth", "dashboard", "finanzas", "fisico", "mental", "negocio", "rutina"]
