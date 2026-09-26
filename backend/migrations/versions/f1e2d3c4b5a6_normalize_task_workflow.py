"""Normalize task workflow: TODO→PLANNED, BLOCKED→ON_HOLD, add CANCELLED; add reason to task_transitions

Revision ID: f1e2d3c4b5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-09-26

Summary of changes:
  1. Migrate existing task status values:
       TODO    → PLANNED
       BLOCKED → ON_HOLD
  2. Extend the task_status_enum with PLANNED, ON_HOLD, CANCELLED
     (drop TODO and BLOCKED from the enum).
  3. Add task_transitions.reason (TEXT, nullable) for ON_HOLD audit trail.
  4. Same data migrations applied to task_transitions.from_status/to_status.

SQLite note: SQLite stores enums as VARCHAR and has no ALTER TYPE.
  All the data updates work on both dialects.
  Enum column changes are a no-op for SQLite (it accepts any string value
  that matches the Python Enum).  PostgreSQL ALTER TYPE is guarded with
  a dialect check.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1e2d3c4b5a6"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # ── 1. Data migration: normalize legacy status values ────────────────────
    op.execute("UPDATE tasks SET status = 'PLANNED' WHERE status = 'TODO'")
    op.execute("UPDATE tasks SET status = 'ON_HOLD' WHERE status = 'BLOCKED'")

    op.execute(
        "UPDATE task_transitions SET from_status = 'PLANNED' WHERE from_status = 'TODO'"
    )
    op.execute(
        "UPDATE task_transitions SET from_status = 'ON_HOLD' WHERE from_status = 'BLOCKED'"
    )
    op.execute(
        "UPDATE task_transitions SET to_status = 'PLANNED' WHERE to_status = 'TODO'"
    )
    op.execute(
        "UPDATE task_transitions SET to_status = 'ON_HOLD' WHERE to_status = 'BLOCKED'"
    )

    # ── 2. PostgreSQL: replace the enum type ─────────────────────────────────
    # SQLite stores enum values as VARCHAR — no ALTER TYPE needed.
    if dialect == "postgresql":
        op.execute("ALTER TYPE task_status_enum RENAME TO task_status_enum_old")
        op.execute(
            "CREATE TYPE task_status_enum AS ENUM "
            "('PLANNED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED')"
        )

        op.execute(
            "ALTER TABLE tasks "
            "ALTER COLUMN status TYPE task_status_enum "
            "USING status::text::task_status_enum"
        )
        op.execute(
            "ALTER TABLE task_transitions "
            "ALTER COLUMN from_status TYPE task_status_enum "
            "USING CASE "
            "WHEN from_status IS NULL THEN NULL "
            "ELSE from_status::text::task_status_enum "
            "END"
        )
        op.execute(
            "ALTER TABLE task_transitions "
            "ALTER COLUMN to_status TYPE task_status_enum "
            "USING to_status::text::task_status_enum"
        )

        op.execute("DROP TYPE task_status_enum_old")

    # ── 3. Add reason column to task_transitions ─────────────────────────────
    # Check if column already exists (idempotent — safe to run multiple times).
    inspector = sa.inspect(bind)
    existing_cols = [col["name"] for col in inspector.get_columns("task_transitions")]
    if "reason" not in existing_cols:
        op.add_column(
            "task_transitions",
            sa.Column("reason", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Remove reason column
    op.drop_column("task_transitions", "reason")

    # Revert data: map new statuses back to legacy vocabulary.
    # CANCELLED has no direct predecessor — map to IN_PROGRESS as the
    # closest active state.
    op.execute("UPDATE tasks SET status = 'TODO' WHERE status = 'PLANNED'")
    op.execute("UPDATE tasks SET status = 'BLOCKED' WHERE status = 'ON_HOLD'")
    op.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE status = 'CANCELLED'")

    op.execute(
        "UPDATE task_transitions SET from_status = 'TODO' WHERE from_status = 'PLANNED'"
    )
    op.execute(
        "UPDATE task_transitions SET from_status = 'BLOCKED' WHERE from_status = 'ON_HOLD'"
    )
    op.execute(
        "UPDATE task_transitions SET from_status = 'IN_PROGRESS' WHERE from_status = 'CANCELLED'"
    )
    op.execute(
        "UPDATE task_transitions SET to_status = 'TODO' WHERE to_status = 'PLANNED'"
    )
    op.execute(
        "UPDATE task_transitions SET to_status = 'BLOCKED' WHERE to_status = 'ON_HOLD'"
    )
    op.execute(
        "UPDATE task_transitions SET to_status = 'IN_PROGRESS' WHERE to_status = 'CANCELLED'"
    )

    if dialect == "postgresql":
        op.execute("ALTER TYPE task_status_enum RENAME TO task_status_enum_new")
        op.execute(
            "CREATE TYPE task_status_enum AS ENUM "
            "('TODO', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED')"
        )

        op.execute(
            "ALTER TABLE tasks "
            "ALTER COLUMN status TYPE task_status_enum "
            "USING status::text::task_status_enum"
        )
        op.execute(
            "ALTER TABLE task_transitions "
            "ALTER COLUMN from_status TYPE task_status_enum "
            "USING CASE "
            "WHEN from_status IS NULL THEN NULL "
            "ELSE from_status::text::task_status_enum "
            "END"
        )
        op.execute(
            "ALTER TABLE task_transitions "
            "ALTER COLUMN to_status TYPE task_status_enum "
            "USING to_status::text::task_status_enum"
        )

        op.execute("DROP TYPE task_status_enum_new")
