"""add user session version

Revision ID: 198b8914fd13
Revises: f1e2d3c4b5a6
Create Date: 2026-10-08 16:46:17.349495

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '198b8914fd13'
down_revision: Union[str, None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('session_version', sa.Integer(), server_default='1', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'session_version')
