"""add foto tables for santri asset and orangtua

Revision ID: a0c591c0b479
Revises: d1a2b3c4d5e6
Create Date: 2025-12-27 21:19:46.114810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0c591c0b479'
down_revision: Union[str, Sequence[str], None] = 'd1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create foto_santri table
    op.create_table('foto_santri',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('nama_file', sa.String(length=255), nullable=False),
        sa.Column('url_photo', sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_foto_santri_santri_id', 'foto_santri', ['santri_id'])
    
    # Create foto_asset table
    op.create_table('foto_asset',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('asset_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('nama_file', sa.String(length=255), nullable=False),
        sa.Column('url_photo', sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['santri_asset.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_foto_asset_asset_id', 'foto_asset', ['asset_id'])
    
    # Create foto_orangtua table
    op.create_table('foto_orangtua',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('orangtua_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('nama_file', sa.String(length=255), nullable=False),
        sa.Column('url_photo', sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(['orangtua_id'], ['santri_orangtua.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_foto_orangtua_orangtua_id', 'foto_orangtua', ['orangtua_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_foto_orangtua_orangtua_id', table_name='foto_orangtua')
    op.drop_table('foto_orangtua')
    
    op.drop_index('idx_foto_asset_asset_id', table_name='foto_asset')
    op.drop_table('foto_asset')
    
    op.drop_index('idx_foto_santri_santri_id', table_name='foto_santri')
    op.drop_table('foto_santri')
