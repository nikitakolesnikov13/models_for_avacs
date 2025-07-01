"""update schema

Revision ID: ec2d199ca39c
Revises: 367f3dbc8a0c
Create Date: 2025-07-01 22:50:33.704570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec2d199ca39c'
down_revision: Union[str, Sequence[str], None] = '367f3dbc8a0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
