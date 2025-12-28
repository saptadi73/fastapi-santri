"""init all santri models with uuid and postgis

Revision ID: d1a2b3c4d5e6
Revises: 
Create Date: 2025-12-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = 'd1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd106442eb02d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')
    
    # Drop old santri and users tables from previous migration
    op.drop_table('users')
    op.drop_table('santri')
    
    # Create santri_pribadi table
    op.create_table('santri_pribadi',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('nama', sa.String(length=150), nullable=False),
        sa.Column('nik', sa.String(length=16), nullable=True),
        sa.Column('no_kk', sa.String(length=16), nullable=True),
        sa.Column('tempat_lahir', sa.String(length=100), nullable=True),
        sa.Column('tanggal_lahir', sa.Date(), nullable=True),
        sa.Column('jenis_kelamin', sa.String(), nullable=False),
        sa.Column('status_tinggal', sa.String(), nullable=True),
        sa.Column('lama_mondok_tahun', sa.Integer(), nullable=True),
        sa.Column('provinsi', sa.String(length=100), nullable=True),
        sa.Column('kabupaten', sa.String(length=100), nullable=True),
        sa.Column('kecamatan', sa.String(length=100), nullable=True),
        sa.Column('desa', sa.String(length=100), nullable=True),
        sa.Column('lokasi', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Note: geoalchemy2 auto-creates GIST index for geometry columns, no explicit index needed
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create santri_bansos table
    op.create_table('santri_bansos',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('pkh', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('bpnt', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('pip', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('kis_pbi', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('blt_desa', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('bantuan_lainnya', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bansos_santri_id', 'santri_bansos', ['santri_id'])
    
    # Create santri_pembiayaan table
    op.create_table('santri_pembiayaan',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('biaya_per_bulan', sa.Integer(), nullable=True),
        sa.Column('sumber_biaya', sa.String(), nullable=True),
        sa.Column('nama_donatur', sa.String(length=150), nullable=True),
        sa.Column('jenis_beasiswa', sa.String(length=100), nullable=True),
        sa.Column('status_pembayaran', sa.String(), nullable=True),
        sa.Column('tunggakan_bulan', sa.Integer(), server_default=sa.literal(0), nullable=False),
        sa.Column('keterangan', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pembiayaan_santri_id', 'santri_pembiayaan', ['santri_id'])
    
    # Create santri_orangtua table
    op.create_table('santri_orangtua',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('nama', sa.String(length=150), nullable=False),
        sa.Column('nik', sa.String(length=16), nullable=True),
        sa.Column('hubungan', sa.String(), nullable=True),
        sa.Column('pendidikan', sa.String(length=50), nullable=True),
        sa.Column('pekerjaan', sa.String(length=100), nullable=True),
        sa.Column('pendapatan_bulanan', sa.Integer(), nullable=True),
        sa.Column('status_hidup', sa.String(), nullable=True),
        sa.Column('kontak_telepon', sa.String(length=15), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_orangtua_santri_id', 'santri_orangtua', ['santri_id'])
    
    # Create santri_kesehatan table
    op.create_table('santri_kesehatan',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('tinggi_badan', sa.Float(), nullable=True),
        sa.Column('berat_badan', sa.Float(), nullable=True),
        sa.Column('status_gizi', sa.String(), nullable=True),
        sa.Column('riwayat_penyakit', sa.String(), nullable=True),
        sa.Column('alergi_obat', sa.String(), nullable=True),
        sa.Column('kebutuhan_khusus', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kesehatan_santri_id', 'santri_kesehatan', ['santri_id'])
    
    # Create santri_rumah table
    op.create_table('santri_rumah',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('status_rumah', sa.String(), nullable=False),
        sa.Column('jenis_lantai', sa.String(), nullable=False),
        sa.Column('jenis_dinding', sa.String(), nullable=False),
        sa.Column('jenis_atap', sa.String(), nullable=False),
        sa.Column('akses_air_bersih', sa.String(), nullable=False),
        sa.Column('daya_listrik_va', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rumah_santri_id', 'santri_rumah', ['santri_id'])
    
    # Create santri_asset table
    op.create_table('santri_asset',
        sa.Column('id', sa.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('santri_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('jenis_aset', sa.String(), nullable=False),
        sa.Column('jumlah', sa.Integer(), server_default=sa.literal(1), nullable=False),
        sa.Column('nilai_perkiraan', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['santri_id'], ['santri_pribadi.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_asset_santri_id', 'santri_asset', ['santri_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_asset_santri_id', table_name='santri_asset')
    op.drop_table('santri_asset')
    
    op.drop_index('idx_rumah_santri_id', table_name='santri_rumah')
    op.drop_table('santri_rumah')
    
    op.drop_index('idx_kesehatan_santri_id', table_name='santri_kesehatan')
    op.drop_table('santri_kesehatan')
    
    op.drop_index('idx_orangtua_santri_id', table_name='santri_orangtua')
    op.drop_table('santri_orangtua')
    
    op.drop_index('idx_pembiayaan_santri_id', table_name='santri_pembiayaan')
    op.drop_table('santri_pembiayaan')
    
    op.drop_index('idx_bansos_santri_id', table_name='santri_bansos')
    op.drop_table('santri_bansos')
    
    # Note: idx_santri_pribadi_lokasi is auto-created by geoalchemy2, will be dropped with table
    op.drop_table('santri_pribadi')
    
    # Recreate old tables
    op.create_table('users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
