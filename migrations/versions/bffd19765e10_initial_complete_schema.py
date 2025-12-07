"""Initial complete schema

Revision ID: bffd19765e10
Revises: 
Create Date: 2025-12-07 00:30:17.207819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bffd19765e10'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Trading Sessions
    op.create_table('trading_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('mode', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('initial_balance', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Account Balance
    op.create_table('account_balance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(length=10), nullable=False),
        sa.Column('cash_balance', sa.Float(), nullable=True),
        sa.Column('total_equity', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['trading_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Strategy Holdings
    op.create_table('strategy_holdings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(length=10), nullable=False),
        sa.Column('strategy_name', sa.String(length=100), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('average_price', sa.Float(), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('unrealized_pnl', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['trading_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_strategy_holdings_strategy_name'), 'strategy_holdings', ['strategy_name'], unique=False)
    op.create_index(op.f('ix_strategy_holdings_ticker'), 'strategy_holdings', ['ticker'], unique=False)
    
    # Trades
    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('fees', sa.Float(), nullable=True),
        sa.Column('order_id', sa.String(length=100), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('strategy_name', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['trading_sessions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    
    # Strategies Config
    op.create_table('strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('class_name', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_strategies_id'), 'strategies', ['id'], unique=False)
    
    # OHLCV
    op.create_table('ohlcv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Float(), nullable=True),
        sa.Column('high', sa.Float(), nullable=True),
        sa.Column('low', sa.Float(), nullable=True),
        sa.Column('close', sa.Float(), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ohlcv_id'), 'ohlcv', ['id'], unique=False)
    op.create_index(op.f('ix_ohlcv_ticker'), 'ohlcv', ['ticker'], unique=False)
    op.create_index(op.f('ix_ohlcv_timestamp'), 'ohlcv', ['timestamp'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_ohlcv_timestamp'), table_name='ohlcv')
    op.drop_index(op.f('ix_ohlcv_ticker'), table_name='ohlcv')
    op.drop_index(op.f('ix_ohlcv_id'), table_name='ohlcv')
    op.drop_table('ohlcv')
    op.drop_index(op.f('ix_strategies_id'), table_name='strategies')
    op.drop_table('strategies')
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')
    op.drop_index(op.f('ix_strategy_holdings_ticker'), table_name='strategy_holdings')
    op.drop_index(op.f('ix_strategy_holdings_strategy_name'), table_name='strategy_holdings')
    op.drop_table('strategy_holdings')
    op.drop_table('account_balance')
    op.drop_table('trading_sessions')

