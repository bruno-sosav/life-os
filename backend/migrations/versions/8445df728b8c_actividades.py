"""actividades definidas por el usuario (reemplazan gym y MMA fijos)

Crea las actividades "Gym" (rutina + lista de ejercicios) y "MMA" (tipo de clase) y les
pasa las sesiones, los ejercicios y el hábito vinculado. Recién después borra las tablas
viejas. El downgrade hace el camino inverso solo para Gym y MMA: las sesiones de otras
actividades se pierden al bajar.

Revision ID: 8445df728b8c
Revises: 587134a4c5b3
Create Date: 2026-11-02 10:32:35.807415

"""

import json
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "8445df728b8c"
down_revision: str | Sequence[str] | None = "587134a4c5b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MMA_TYPES = ["técnica", "sparring", "grappling", "libre"]


def _field(name: str, type_: str, options: list[str] | None = None) -> dict[str, object]:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": type_,
        "unit": None,
        "options": options,
        "archived": False,
    }


def _linked_habit(conn: sa.Connection, module: str) -> str | None:
    return conn.execute(
        sa.text(
            "SELECT id FROM habits WHERE linked_module = :m AND active "
            "ORDER BY sort_order, created_at LIMIT 1"
        ),
        {"m": module},
    ).scalar()


def _move_data() -> None:
    conn = op.get_bind()
    routine = _field("Rutina", "texto")
    gym = {"id": str(uuid.uuid4()), "name": "Gym", "emoji": "🏋️", "color": "#BF5AF2"}
    gym["fields"] = [routine, _field("Ejercicios", "ejercicios")]
    used = conn.execute(sa.text("SELECT DISTINCT session_type FROM mma_sessions")).scalars()
    kind = _field("Tipo", "opcion", MMA_TYPES + [t for t in used if t and t not in MMA_TYPES])
    mma = {"id": str(uuid.uuid4()), "name": "MMA", "emoji": "🥊", "color": "#FF453A"}
    mma["fields"] = [kind]

    for order, (activity, module) in enumerate(((gym, "gym"), (mma, "mma"))):
        conn.execute(
            sa.text(
                "INSERT INTO activities (id, name, emoji, color, active, sort_order, fields, "
                "habit_id) VALUES (:id, :name, :emoji, :color, 1, :order, :fields, :habit)"
            ),
            {
                **activity,
                "order": order,
                "fields": json.dumps(activity["fields"]),
                "habit": _linked_habit(conn, module),
            },
        )

    conn.execute(
        sa.text(
            "INSERT INTO activity_sessions "
            "(id, activity_id, date, attended, notes, `values`, created_at) "
            "SELECT id, :activity, date, attended, notes, "
            "IF(routine_name IS NULL OR routine_name = '', JSON_OBJECT(), "
            "JSON_OBJECT(:field, routine_name)), created_at FROM gym_sessions"
        ),
        {"activity": gym["id"], "field": routine["id"]},
    )
    conn.execute(
        sa.text(
            "INSERT INTO session_exercises "
            "(id, session_id, exercise_name, sets, reps, weight_kg, notes) "
            "SELECT id, session_id, exercise_name, sets, reps, weight_kg, notes "
            "FROM gym_exercises"
        )
    )
    conn.execute(
        sa.text(
            "INSERT INTO activity_sessions "
            "(id, activity_id, date, attended, notes, `values`, created_at) "
            "SELECT id, :activity, date, attended, notes, "
            "IF(session_type IS NULL OR session_type = '', JSON_OBJECT(), "
            "JSON_OBJECT(:field, session_type)), created_at FROM mma_sessions"
        ),
        {"activity": mma["id"], "field": kind["id"]},
    )


def _move_back() -> None:
    conn = op.get_bind()
    for name, module, table, column in (
        ("Gym", "gym", "gym_sessions", "routine_name"),
        ("MMA", "mma", "mma_sessions", "session_type"),
    ):
        row = conn.execute(
            sa.text("SELECT id, fields, habit_id FROM activities WHERE name = :n LIMIT 1"),
            {"n": name},
        ).first()
        if row is None:
            continue
        activity_id, fields, habit_id = row
        fields = json.loads(fields) if isinstance(fields, str) else fields
        text_field = next(
            (f["id"] for f in fields if f["type"] in ("texto", "opcion")), "sin-campo"
        )
        conn.execute(
            sa.text(
                f"INSERT INTO {table} (id, date, attended, {column}, notes, created_at) "
                "SELECT id, date, attended, "
                "JSON_UNQUOTE(JSON_EXTRACT(`values`, CONCAT('$.\"', :field, '\"'))), "
                "notes, created_at FROM activity_sessions WHERE activity_id = :activity"
            ),
            {"field": text_field, "activity": activity_id},
        )
        if module == "gym":
            conn.execute(
                sa.text(
                    "INSERT INTO gym_exercises "
                    "(id, session_id, exercise_name, sets, reps, weight_kg, notes) "
                    "SELECT e.id, e.session_id, e.exercise_name, e.sets, e.reps, e.weight_kg, "
                    "e.notes FROM session_exercises e JOIN activity_sessions s "
                    "ON s.id = e.session_id WHERE s.activity_id = :activity"
                ),
                {"activity": activity_id},
            )
        if habit_id:
            conn.execute(
                sa.text("UPDATE habits SET linked_module = :m WHERE id = :h"),
                {"m": module, "h": habit_id},
            )


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "activities",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("emoji", sa.String(length=32), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("fields", sa.JSON(), nullable=False),
        sa.Column("habit_id", sa.CHAR(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["habit_id"],
            ["habits.id"],
            name=op.f("fk_activities_habit_id_habits"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activities")),
    )
    op.create_table(
        "activity_sessions",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("activity_id", sa.CHAR(length=36), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("attended", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
            name=op.f("fk_activity_sessions_activity_id_activities"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activity_sessions")),
    )
    op.create_index(
        op.f("ix_activity_sessions_activity_id"), "activity_sessions", ["activity_id"], unique=False
    )
    op.create_index(op.f("ix_activity_sessions_date"), "activity_sessions", ["date"], unique=False)
    op.create_table(
        "session_exercises",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("session_id", sa.CHAR(length=36), nullable=False),
        sa.Column("exercise_name", sa.String(length=255), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["activity_sessions.id"],
            name=op.f("fk_session_exercises_session_id_activity_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session_exercises")),
    )
    op.create_index(
        op.f("ix_session_exercises_session_id"), "session_exercises", ["session_id"], unique=False
    )
    _move_data()
    # Sin drop_index: MySQL no deja borrar el índice de una FK, y drop_table ya los borra
    op.drop_table("gym_exercises")
    op.drop_table("gym_sessions")
    op.drop_table("mma_sessions")
    op.drop_column("habits", "linked_module")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("habits", sa.Column("linked_module", mysql.VARCHAR(length=20), nullable=True))
    op.create_table(
        "mma_sessions",
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.Column("date", sa.DATE(), nullable=False),
        sa.Column("attended", mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column("session_type", mysql.VARCHAR(length=255), nullable=True),
        sa.Column("notes", mysql.TEXT(), nullable=True),
        sa.Column(
            "created_at", mysql.DATETIME(), server_default=sa.text("(now())"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(op.f("ix_mma_sessions_date"), "mma_sessions", ["date"], unique=False)
    op.create_table(
        "gym_sessions",
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.Column("date", sa.DATE(), nullable=False),
        sa.Column("attended", mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column("routine_name", mysql.VARCHAR(length=255), nullable=True),
        sa.Column("notes", mysql.TEXT(), nullable=True),
        sa.Column(
            "created_at", mysql.DATETIME(), server_default=sa.text("(now())"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(op.f("ix_gym_sessions_date"), "gym_sessions", ["date"], unique=False)
    op.create_table(
        "gym_exercises",
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.Column("session_id", mysql.CHAR(length=36), nullable=False),
        sa.Column("exercise_name", mysql.VARCHAR(length=255), nullable=False),
        sa.Column("sets", mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("reps", mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("weight_kg", mysql.DECIMAL(precision=6, scale=2), nullable=True),
        sa.Column("notes", mysql.TEXT(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["gym_sessions.id"],
            name=op.f("fk_gym_exercises_session_id_gym_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(
        op.f("ix_gym_exercises_session_id"), "gym_exercises", ["session_id"], unique=False
    )
    _move_back()
    op.drop_table("session_exercises")
    op.drop_table("activity_sessions")
    op.drop_table("activities")
