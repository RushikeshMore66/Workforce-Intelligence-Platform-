"""add_work_update_creator

Revision ID: 987e1ddf1ae1
Revises: cbe632974f17
Create Date: 2026-09-07 22:49:51.991451

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '987e1ddf1ae1'
down_revision: Union[str, None] = 'cbe632974f17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('work_updates', sa.Column('created_by_user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_work_updates_created_by_user_id'), 'work_updates', ['created_by_user_id'], unique=False)
    op.create_foreign_key('fk_work_updates_created_by_user_id', 'work_updates', 'users', ['created_by_user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_work_updates_created_by_user_id', 'work_updates', type_='foreignkey')
    op.drop_index(op.f('ix_work_updates_created_by_user_id'), table_name='work_updates')
    op.drop_column('work_updates', 'created_by_user_id')
