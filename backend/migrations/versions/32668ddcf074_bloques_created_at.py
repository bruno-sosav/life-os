"""bloques de rutina con created_at

Un bloque semanal cuenta para la racha desde que se crea. Los que ya existían
quedan con una fecha vieja para que sigan contando en el pasado.

Revision ID: 32668ddcf074
Revises: bf24e6aaaf16
Create Date: 2026-10-27 19:10:36.181415

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32668ddcf074"
down_revision: str | Sequence[str] | None = "bf24e6aaaf16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "routine_blocks",
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.execute("UPDATE routine_blocks SET created_at = '2000-01-01'")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("routine_blocks", "created_at")
