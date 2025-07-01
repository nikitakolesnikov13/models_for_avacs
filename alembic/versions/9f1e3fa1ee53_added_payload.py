"""added payload

Revision ID: 9f1e3fa1ee53
Revises: c4d2ec10fe80
Create Date: 2025-07-01 22:42:50.723557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f1e3fa1ee53'
down_revision: Union[str, Sequence[str], None] = 'c4d2ec10fe80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
