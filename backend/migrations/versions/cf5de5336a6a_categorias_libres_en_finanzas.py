"""categorías y fuentes libres en finanzas

Las categorías de gasto y las fuentes de ingreso fijas pasan a guardarse como se ven
("🍔 Comida", "Sueldo"). Desde acá se puede usar cualquiera. El downgrade vuelve a las
fijas y manda el resto a "otro".

Revision ID: cf5de5336a6a
Revises: 3fe78b1918b7
Create Date: 2026-11-02 12:19:32.294948

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf5de5336a6a"
down_revision: str | Sequence[str] | None = "3fe78b1918b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


CATEGORIES = {
    "comida": "🍔 Comida",
    "transporte": "🚗 Transporte",
    "salud": "💊 Salud",
    "ocio": "🎮 Ocio",
    "ropa": "👕 Ropa",
    "educacion": "📚 Educación",
    "servicios": "💡 Servicios",
    "suscripciones": "📱 Suscripciones",
    "otro": "📦 Otro",
}
SOURCES = {
    "sueldo": "Sueldo",
    "freelance": "Freelance",
    "inversión": "Inversión",
    "regalo": "Regalo",
    "otro": "Otro",
}


def _rename(table: str, column: str, mapping: dict[str, str], default: str | None = None) -> None:
    cases = " ".join(f"WHEN :old{i} THEN :new{i}" for i in range(len(mapping)))
    params = {}
    for i, (old, new) in enumerate(mapping.items()):
        params[f"old{i}"], params[f"new{i}"] = old, new
    fallback = column
    if default:
        fallback, params["default"] = ":default", default
    op.get_bind().execute(
        sa.text(
            f"UPDATE {table} SET {column} = CASE {column} {cases} ELSE {fallback} END "
            f"WHERE {column} IS NOT NULL"
        ),
        params,
    )


def upgrade() -> None:
    _rename("finance_expenses", "category", CATEGORIES)
    _rename("finance_income", "source", SOURCES)


def downgrade() -> None:
    _rename("finance_expenses", "category", {v: k for k, v in CATEGORIES.items()}, "otro")
    _rename("finance_income", "source", {v: k for k, v in SOURCES.items()}, "otro")
