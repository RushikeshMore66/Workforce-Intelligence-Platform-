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
    with op.batch_alter_table('work_updates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_user_id', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_work_updates_created_by_user_id'), ['created_by_user_id'], unique=False)
        batch_op.create_foreign_key('fk_work_updates_created_by_user_id', 'users', ['created_by_user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    with op.batch_alter_table('work_updates', schema=None) as batch_op:
        batch_op.drop_constraint('fk_work_updates_created_by_user_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_work_updates_created_by_user_id'))
        batch_op.drop_column('created_by_user_id')
