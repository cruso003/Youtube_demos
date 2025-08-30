"""Add service_configurations table for business adapters

Revision ID: add_service_configurations
Revises: de2d669e75d7
Create Date: 2025-08-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_service_configurations'
down_revision: Union[str, Sequence[str], None] = 'de2d669e75d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add service_configurations table"""
    op.create_table('service_configurations',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.UUID(), nullable=False, index=True),
        sa.Column('business_adapter', sa.String(), nullable=False, index=True),
        sa.Column('config_name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('config_data', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id', 'business_adapter', 'config_name', name='unique_user_adapter_config')
    )

def downgrade() -> None:
    """Remove service_configurations table"""
    op.drop_table('service_configurations')