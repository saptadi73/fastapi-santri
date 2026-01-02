"""Add missing columns to match API documentation schema

Revision ID: 20260101_add_missing_columns
Revises: add_rasio_kamar
Create Date: 2026-01-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260101_add_missing_columns'
down_revision: Union[str, Sequence[str], None] = ['add_rasio_kamar', '20250101_add_map_tables']
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to match API documentation."""
    
    # 1. Add missing columns to pesantren_fasilitas
    op.add_column('pesantren_fasilitas',
        sa.Column('jumlah_kamar_mandi', sa.Integer(), nullable=True)
    )
    op.add_column('pesantren_fasilitas',
        sa.Column('sumber_air', sa.String(), nullable=True)
    )
    
    # 2. Fix pesantren_skor - rename/add correct columns
    # Rename existing columns to match schema
    op.alter_column('pesantren_skor', 'skor_kelayakan_fisik',
        new_column_name='skor_fisik', existing_type=sa.Integer())
    
    op.add_column('pesantren_skor',
        sa.Column('skor_fasilitas', sa.Integer(), nullable=True)
    )
    op.add_column('pesantren_skor',
        sa.Column('skor_pendidikan', sa.Integer(), nullable=True)
    )
    
    # Remove redundant columns from pesantren_skor if they're just aliases
    # Keep: skor_fisik (renamed from skor_kelayakan_fisik)
    # Keep: skor_fasilitas (new)
    # Keep: skor_pendidikan (new)
    # Remove: skor_air_sanitasi, skor_fasilitas_pendukung (deprecated)
    
    # 3. Add missing column to pondok_pesantren
    op.add_column('pondok_pesantren',
        sa.Column('kontak_telepon', sa.String(15), nullable=True)
    )
    # Note: telepon already exists, kontak_telepon is alias/additional field
    
    # 4. Add missing column to santri table
    op.add_column('santri',
        sa.Column('status', sa.String(), nullable=True)
    )
    
    # 5. Add missing column to santri_pembiayaan
    op.add_column('santri_pembiayaan',
        sa.Column('sumber_pembiayaan', sa.String(), nullable=True)
    )
    # Note: sumber_biaya exists, sumber_pembiayaan is standardized name
    
    # 6. Add missing columns to santri_pribadi (latitude, longitude)
    op.add_column('santri_pribadi',
        sa.Column('latitude', sa.Float(), nullable=True)
    )
    op.add_column('santri_pribadi',
        sa.Column('longitude', sa.Float(), nullable=True)
    )
    
    # 7. Add missing columns to santri_skor (timestamps)
    op.add_column('santri_skor',
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True)
    )
    op.add_column('santri_skor',
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade: remove added columns."""
    
    # Remove from santri_skor
    op.drop_column('santri_skor', 'updated_at')
    op.drop_column('santri_skor', 'created_at')
    
    # Remove from santri_pribadi
    op.drop_column('santri_pribadi', 'longitude')
    op.drop_column('santri_pribadi', 'latitude')
    
    # Remove from santri_pembiayaan
    op.drop_column('santri_pembiayaan', 'sumber_pembiayaan')
    
    # Remove from santri
    op.drop_column('santri', 'status')
    
    # Remove from pondok_pesantren
    op.drop_column('pondok_pesantren', 'kontak_telepon')
    
    # Remove from pesantren_skor
    op.drop_column('pesantren_skor', 'skor_pendidikan')
    op.drop_column('pesantren_skor', 'skor_fasilitas')
    op.alter_column('pesantren_skor', 'skor_fisik',
        new_column_name='skor_kelayakan_fisik', existing_type=sa.Integer())
    
    # Remove from pesantren_fasilitas
    op.drop_column('pesantren_fasilitas', 'sumber_air')
    op.drop_column('pesantren_fasilitas', 'jumlah_kamar_mandi')
