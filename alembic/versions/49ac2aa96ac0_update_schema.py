"""update schema

Revision ID: 49ac2aa96ac0
Revises: ec2d199ca39c
Create Date: 2025-07-01 22:55:15.568595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49ac2aa96ac0'
down_revision: Union[str, Sequence[str], None] = 'ec2d199ca39c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
