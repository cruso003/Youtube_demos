"""Add api_key_services table for service-specific API key configurations

Revision ID: add_api_key_services  
Revises: add_service_configurations
Create Date: 2025-08-30 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_api_key_services'
down_revision: Union[str, Sequence[str], None] = 'add_service_configurations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add api_key_services table for service-specific configurations"""
    op.create_table('api_key_services',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('api_key', sa.String(), nullable=False, index=True),
        sa.Column('user_id', sa.UUID(), nullable=False, index=True),
        sa.Column('service_type', sa.String(), nullable=False), # 'gpt', 'voice_tts', 'voice_stt', etc.
        sa.Column('provider', sa.String(), nullable=False),     # 'cartesia', 'deepgram', 'twilio', etc.
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('cost_limits', postgresql.JSON(), nullable=True), # Per-service cost limits
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['api_key'], ['api_keys.api_key']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('api_key', 'service_type', name='unique_key_service')
    )

def downgrade() -> None:
    """Remove api_key_services table"""
    op.drop_table('api_key_services')