"""update schema with payload

Revision ID: 367f3dbc8a0c
Revises: f980ed761cd4
Create Date: 2025-07-01 22:48:33.649913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '367f3dbc8a0c'
down_revision: Union[str, Sequence[str], None] = 'f980ed761cd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
