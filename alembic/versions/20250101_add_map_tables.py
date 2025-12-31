"""Add santri_map and pesantren_map tables for GIS mapping.

Revision ID: 20250101_add_map_tables
Revises: 
Create Date: 2025-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = '20250101_add_map_tables'
down_revision = '2f6367300e75'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Create santri_map and pesantren_map tables."""
    
    # Create santri_map table
    op.create_table(
        'santri_map',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('santri_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('nama', sa.String(150), nullable=False),
        sa.Column('skor_terakhir', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('kategori_kemiskinan', sa.String(50), nullable=False, server_default='Tidak Miskin'),
        sa.Column('lokasi', Geometry('POINT', srid=4326), nullable=True),
        sa.Column('pesantren_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pesantren_id'], ['pondok_pesantren.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for santri_map
    op.create_index('idx_santri_map_santri_id', 'santri_map', ['santri_id'])
    op.create_index('idx_santri_map_nama', 'santri_map', ['nama'])
    op.create_index('idx_santri_map_pesantren_id', 'santri_map', ['pesantren_id'])
    op.create_index('idx_santri_map_kategori', 'santri_map', ['kategori_kemiskinan'])
    op.execute('CREATE INDEX idx_santri_map_lokasi ON santri_map USING GIST (lokasi)')
    
    # Create pesantren_map table
    op.create_table(
        'pesantren_map',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pesantren_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('nama', sa.String(200), nullable=False),
        sa.Column('nsp', sa.String(50), nullable=True),
        sa.Column('skor_terakhir', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('kategori_kelayakan', sa.String(50), nullable=False, server_default='tidak_layak'),
        sa.Column('lokasi', Geometry('POINT', srid=4326), nullable=True),
        sa.Column('kabupaten', sa.String(100), nullable=True),
        sa.Column('provinsi', sa.String(100), nullable=True),
        sa.Column('jumlah_santri', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['pesantren_id'], ['pondok_pesantren.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for pesantren_map
    op.create_index('idx_pesantren_map_pesantren_id', 'pesantren_map', ['pesantren_id'])
    op.create_index('idx_pesantren_map_nama', 'pesantren_map', ['nama'])
    op.create_index('idx_pesantren_map_kabupaten', 'pesantren_map', ['kabupaten'])
    op.create_index('idx_pesantren_map_provinsi', 'pesantren_map', ['provinsi'])
    op.create_index('idx_pesantren_map_kategori', 'pesantren_map', ['kategori_kelayakan'])
    op.execute('CREATE INDEX idx_pesantren_map_lokasi ON pesantren_map USING GIST (lokasi)')


def downgrade():
    """Drop santri_map and pesantren_map tables."""
    op.drop_table('santri_map')
    op.drop_table('pesantren_map')
