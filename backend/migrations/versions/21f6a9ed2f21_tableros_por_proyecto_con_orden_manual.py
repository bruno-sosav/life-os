"""tableros por proyecto con orden manual

Toda tarea pasa a vivir en un proyecto (las sueltas van a "General") y tiene un lugar
dentro de su columna. El orden inicial es el que mostraba el tablero: prioridad y
vencimiento.

Revision ID: 21f6a9ed2f21
Revises: f223a57edfd2
Create Date: 2026-11-04 11:46:02.047180

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "21f6a9ed2f21"
down_revision: str | Sequence[str] | None = "f223a57edfd2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


FK = "fk_stratus_tasks_project_id_projects"
PRIORITY_RANK = {"alta": 0, "media": 1, "baja": 2}


def _foreign_key(ondelete: str) -> None:
    op.create_foreign_key(
        op.f(FK), "stratus_tasks", "projects", ["project_id"], ["id"], ondelete=ondelete
    )


def upgrade() -> None:
    conn = op.get_bind()
    op.add_column(
        "stratus_tasks",
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("stratus_tasks", "position", existing_type=sa.Integer(), server_default=None)

    orphans = conn.execute(sa.text("SELECT COUNT(*) FROM stratus_tasks WHERE project_id IS NULL"))
    if orphans.scalar():
        general = str(uuid.uuid4())
        conn.execute(
            sa.text(
                "INSERT INTO projects (id, name, color, emoji, created_at) "
                "VALUES (:id, 'General', '#8C948F', NULL, NOW())"
            ),
            {"id": general},
        )
        conn.execute(
            sa.text("UPDATE stratus_tasks SET project_id = :id WHERE project_id IS NULL"),
            {"id": general},
        )

    rows = conn.execute(
        sa.text("SELECT id, project_id, status, priority, due_date, created_at FROM stratus_tasks")
    ).all()
    columns: dict[tuple[str, str], list[sa.Row]] = {}
    for row in rows:
        columns.setdefault((row.project_id, row.status), []).append(row)
    for tasks in columns.values():
        tasks.sort(key=lambda r: r.created_at, reverse=True)
        tasks.sort(key=lambda r: (PRIORITY_RANK.get(r.priority, 1), r.due_date is None, r.due_date))
        for position, row in enumerate(tasks):
            conn.execute(
                sa.text("UPDATE stratus_tasks SET position = :p WHERE id = :id"),
                {"p": position, "id": row.id},
            )

    # MySQL no deja hacer NOT NULL una columna con una FK ON DELETE SET NULL: primero la FK
    op.drop_constraint(op.f(FK), "stratus_tasks", type_="foreignkey")
    op.alter_column(
        "stratus_tasks", "project_id", existing_type=mysql.CHAR(length=36), nullable=False
    )
    _foreign_key("CASCADE")


def downgrade() -> None:
    """Las tareas que se pasaron a "General" se quedan ahí."""
    op.drop_constraint(op.f(FK), "stratus_tasks", type_="foreignkey")
    op.alter_column(
        "stratus_tasks", "project_id", existing_type=mysql.CHAR(length=36), nullable=True
    )
    _foreign_key("SET NULL")
    op.drop_column("stratus_tasks", "position")
