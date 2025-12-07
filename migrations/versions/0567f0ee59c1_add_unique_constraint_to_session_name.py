"""Add unique constraint to session name

Revision ID: 0567f0ee59c1
Revises: bffd19765e10
Create Date: 2025-12-07 00:46:15.693405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0567f0ee59c1'
down_revision: Union[str, Sequence[str], None] = 'bffd19765e10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint to name column
    op.create_unique_constraint('uq_trading_sessions_name', 'trading_sessions', ['name'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraint
    op.drop_constraint('uq_trading_sessions_name', 'trading_sessions', type_='unique')

