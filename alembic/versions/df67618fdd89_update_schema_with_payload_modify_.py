"""update schema with payload, modify context and flights

Revision ID: df67618fdd89
Revises: e56737bf1bbb
Create Date: 2025-07-01 22:45:49.166504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df67618fdd89'
down_revision: Union[str, Sequence[str], None] = 'e56737bf1bbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
