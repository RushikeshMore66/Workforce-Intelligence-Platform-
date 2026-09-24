"""Add is_active to users and user_audit_logs table

Revision ID: a1b2c3d4e5f6
Revises: c44abb9df33c
Create Date: 2026-09-24 22:00:00.000000

Changes:
  1. users.is_active  (Boolean, NOT NULL, DEFAULT TRUE, indexed)
     - All existing rows set to TRUE via server_default
     - Deactivated users cannot authenticate
  2. user_audit_logs table for account lifecycle events
     - USER_CREATED, USER_UPDATED, USER_ACTIVATED, USER_DEACTIVATED,
       PASSWORD_CHANGED
  3. Add USER_ACTIVATED, USER_DEACTIVATED, PASSWORD_CHANGED values to
     the activity_type_enum (for completeness; the user_audit_logs table
     is the primary audit mechanism for account events).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e06e69fd8b2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_active to users
    # server_default ensures existing rows get TRUE without a full table scan.
    # sa.true() generates the correct literal for both PostgreSQL ('true') and SQLite ('1').
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    # 2. Extend the activity_type_enum with lifecycle events.
    # SQLite does not support ALTER TYPE; for SQLite we recreate as a plain string
    # comparison.  For PostgreSQL, use op.execute to add enum values.
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute("ALTER TYPE activity_type_enum ADD VALUE IF NOT EXISTS 'USER_ACTIVATED'")
        op.execute("ALTER TYPE activity_type_enum ADD VALUE IF NOT EXISTS 'USER_DEACTIVATED'")
        op.execute("ALTER TYPE activity_type_enum ADD VALUE IF NOT EXISTS 'PASSWORD_CHANGED'")
    # SQLite stores enum values as VARCHAR, no ALTER required.

    # 3. Create user_audit_logs table
    op.create_table(
        "user_audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("target_user_id", sa.String(), nullable=True),
        sa.Column("actor_user_id", sa.String(), nullable=True),
        sa.Column("actor_name", sa.String(), nullable=False),
        sa.Column(
            "event",
            sa.Enum(
                "USER_CREATED",
                "USER_UPDATED",
                "USER_ACTIVATED",
                "USER_DEACTIVATED",
                "PASSWORD_CHANGED",
                name="user_audit_event_enum",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_audit_logs_id"), "user_audit_logs", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_user_audit_logs_target_user_id"),
        "user_audit_logs",
        ["target_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_audit_logs_actor_user_id"),
        "user_audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_audit_logs_event"), "user_audit_logs", ["event"], unique=False
    )
    op.create_index(
        op.f("ix_user_audit_logs_timestamp"),
        "user_audit_logs",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    # Drop user_audit_logs
    op.drop_index(op.f("ix_user_audit_logs_timestamp"), table_name="user_audit_logs")
    op.drop_index(op.f("ix_user_audit_logs_event"), table_name="user_audit_logs")
    op.drop_index(
        op.f("ix_user_audit_logs_actor_user_id"), table_name="user_audit_logs"
    )
    op.drop_index(
        op.f("ix_user_audit_logs_target_user_id"), table_name="user_audit_logs"
    )
    op.drop_index(op.f("ix_user_audit_logs_id"), table_name="user_audit_logs")
    op.drop_table("user_audit_logs")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS user_audit_event_enum")

    # Remove is_active from users
    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_column("users", "is_active")
