"""etiquetas libres en ideas

Las 5 etiquetas fijas pasan a guardarse como se ven ("💬 Frase"). Desde acá cada idea
puede tener cualquier etiqueta. El downgrade vuelve a las 5 y manda el resto a "idea".

Revision ID: 3fe78b1918b7
Revises: 8445df728b8c
Create Date: 2026-11-02 11:24:11.867457

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3fe78b1918b7"
down_revision: str | Sequence[str] | None = "8445df728b8c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TAGS = {
    "frase": "💬 Frase",
    "idea de negocio": "💼 Negocio",
    "aprendizaje": "📚 Aprendizaje",
    "meta": "🎯 Meta",
    "idea": "💡 Idea",
}


def _rename(mapping: dict[str, str], default: str | None = None) -> None:
    cases = " ".join(f"WHEN :old{i} THEN :new{i}" for i in range(len(mapping)))
    params = {}
    for i, (old, new) in enumerate(mapping.items()):
        params[f"old{i}"], params[f"new{i}"] = old, new
    fallback = ":default" if default else "tag"
    if default:
        params["default"] = default
    op.get_bind().execute(
        sa.text(f"UPDATE ideas SET tag = CASE tag {cases} ELSE {fallback} END"), params
    )


def upgrade() -> None:
    _rename(TAGS)


def downgrade() -> None:
    _rename({new: old for old, new in TAGS.items()}, default="idea")
