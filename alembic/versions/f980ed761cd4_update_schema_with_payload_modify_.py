"""update schema with payload, modify context and flights

Revision ID: f980ed761cd4
Revises: df67618fdd89
Create Date: 2025-07-01 22:48:25.160790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f980ed761cd4'
down_revision: Union[str, Sequence[str], None] = 'df67618fdd89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
