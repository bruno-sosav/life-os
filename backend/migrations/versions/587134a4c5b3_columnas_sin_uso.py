"""columnas sin uso

habits.icon y habit_logs.note nunca se escribían; routine_completions.completed siempre era
true (desmarcar borra la fila); routine_blocks.day_of_week repetía days_of_week.

Revision ID: 587134a4c5b3
Revises: 32668ddcf074
Create Date: 2026-10-27 19:17:47.271966

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "587134a4c5b3"
down_revision: str | Sequence[str] | None = "32668ddcf074"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Bloques viejos que solo tenían day_of_week: pasa a days_of_week antes de borrarla
    op.execute(
        "UPDATE routine_blocks SET days_of_week = JSON_ARRAY(day_of_week) "
        "WHERE day_of_week IS NOT NULL "
        "AND (days_of_week IS NULL OR JSON_LENGTH(days_of_week) = 0)"
    )
    op.drop_column("habit_logs", "note")
    op.drop_column("habits", "icon")
    op.drop_column("routine_blocks", "day_of_week")
    op.drop_column("routine_completions", "completed")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "routine_completions",
        sa.Column(
            "completed",
            mysql.TINYINT(display_width=1),
            server_default=sa.text("1"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "routine_blocks",
        sa.Column("day_of_week", mysql.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column("habits", sa.Column("icon", mysql.VARCHAR(length=32), nullable=True))
    op.add_column("habit_logs", sa.Column("note", mysql.TEXT(), nullable=True))
