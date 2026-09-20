"""normalize task workflow statuses

Revision ID: b7f4c2d91a10
Revises: e06e69fd8b2e
Create Date: 2026-09-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7f4c2d91a10"
down_revision: Union[str, None] = "e06e69fd8b2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Normalize legacy values before replacing the PostgreSQL enum.
    op.execute("UPDATE tasks SET status = 'PLANNED' WHERE status = 'TODO'")
    op.execute("UPDATE tasks SET status = 'ON_HOLD' WHERE status = 'BLOCKED'")
    op.execute("UPDATE task_transitions SET from_status = 'PLANNED' WHERE from_status = 'TODO'")
    op.execute("UPDATE task_transitions SET from_status = 'ON_HOLD' WHERE from_status = 'BLOCKED'")
    op.execute("UPDATE task_transitions SET to_status = 'PLANNED' WHERE to_status = 'TODO'")
    op.execute("UPDATE task_transitions SET to_status = 'ON_HOLD' WHERE to_status = 'BLOCKED'")

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

    op.add_column(
        "task_transitions",
        sa.Column("reason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("task_transitions", "reason")

    # Map new states back to the legacy vocabulary.
    op.execute("UPDATE tasks SET status = 'TODO' WHERE status = 'PLANNED'")
    op.execute("UPDATE tasks SET status = 'BLOCKED' WHERE status = 'ON_HOLD'")
    op.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE status = 'CANCELLED'")
    op.execute("UPDATE task_transitions SET from_status = 'TODO' WHERE from_status = 'PLANNED'")
    op.execute("UPDATE task_transitions SET from_status = 'BLOCKED' WHERE from_status = 'ON_HOLD'")
    op.execute("UPDATE task_transitions SET from_status = 'IN_PROGRESS' WHERE from_status = 'CANCELLED'")
    op.execute("UPDATE task_transitions SET to_status = 'TODO' WHERE to_status = 'PLANNED'")
    op.execute("UPDATE task_transitions SET to_status = 'BLOCKED' WHERE to_status = 'ON_HOLD'")
    op.execute("UPDATE task_transitions SET to_status = 'IN_PROGRESS' WHERE to_status = 'CANCELLED'")

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
