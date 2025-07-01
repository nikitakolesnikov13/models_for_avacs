"""update schema with payload, modify context and flights

Revision ID: e56737bf1bbb
Revises: 9f1e3fa1ee53
Create Date: 2025-07-01 22:43:19.967006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e56737bf1bbb'
down_revision: Union[str, Sequence[str], None] = '9f1e3fa1ee53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
