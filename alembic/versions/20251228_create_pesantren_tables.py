"""create pesantren tables

Revision ID: 20251228_create_pesantren
Revises: 20251228_add_pesantren_skor
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = "create_pesantren"
down_revision: Union[str, Sequence[str], None] = "santri_skor_20251228"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all pesantren tables."""
    
    # Create pondok_pesantren table
    op.create_table(
        "pondok_pesantren",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("nama", sa.String(length=200), nullable=False),
        sa.Column("nsp", sa.String(length=20), nullable=True),
        sa.Column("alamat", sa.String(), nullable=True),
        sa.Column("desa", sa.String(length=100), nullable=True),
        sa.Column("kecamatan", sa.String(length=100), nullable=True),
        sa.Column("kabupaten", sa.String(length=100), nullable=True),
        sa.Column("provinsi", sa.String(length=100), nullable=True),
        sa.Column("kode_pos", sa.String(length=10), nullable=True),
        sa.Column("lokasi", geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("telepon", sa.String(length=15), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("website", sa.String(length=100), nullable=True),
        sa.Column("nama_kyai", sa.String(length=150), nullable=True),
        sa.Column("jumlah_santri", sa.Integer(), nullable=True),
        sa.Column("jumlah_guru", sa.Integer(), nullable=True),
        sa.Column("tahun_berdiri", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("idx_pondok_pesantren_nama", "pondok_pesantren", ["nama"])
    op.create_index("idx_pondok_pesantren_kabupaten", "pondok_pesantren", ["kabupaten"])
    
    # Create pesantren_fisik table
    op.create_table(
        "pesantren_fisik",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("luas_tanah", sa.Float(), nullable=True),
        sa.Column("luas_bangunan", sa.Float(), nullable=True),
        sa.Column("status_bangunan", sa.String(), nullable=True),
        sa.Column("kondisi_bangunan", sa.String(), nullable=True),
        sa.Column("sumber_air", sa.String(), nullable=True),
        sa.Column("kualitas_air_bersih", sa.String(), nullable=True),
        sa.Column("fasilitas_mck", sa.String(), nullable=True),
        sa.Column("jumlah_mck", sa.Integer(), nullable=True),
        sa.Column("jenis_lantai", sa.String(), nullable=True),
        sa.Column("jenis_dinding", sa.String(), nullable=True),
        sa.Column("jenis_atap", sa.String(), nullable=True),
        sa.Column("sumber_listrik", sa.String(), nullable=True),
        sa.Column("daya_listrik_va", sa.String(length=20), nullable=True),
        sa.Column("kestabilan_listrik", sa.String(), nullable=True),
        sa.Column("sistem_keamanan", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pesantren_id")
    )
    op.create_index("idx_pesantren_fisik_pesantren_id", "pesantren_fisik", ["pesantren_id"])
    
    # Create pesantren_fasilitas table
    op.create_table(
        "pesantren_fasilitas",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("jumlah_kamar", sa.Integer(), nullable=True),
        sa.Column("jumlah_ruang_kelas", sa.Integer(), nullable=True),
        sa.Column("jumlah_masjid", sa.Integer(), nullable=True),
        sa.Column("perpustakaan", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("laboratorium", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("ruang_komputer", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("fasilitas_olahraga", sa.String(), nullable=True),
        sa.Column("fasilitas_kesehatan", sa.String(), nullable=True),
        sa.Column("koperasi", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("kantin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("fasilitas_mengajar", sa.String(), nullable=True),
        sa.Column("fasilitas_komunikasi", sa.String(), nullable=True),
        sa.Column("akses_transportasi", sa.String(), nullable=True),
        sa.Column("akses_jalan", sa.String(), nullable=True),
        sa.Column("jarak_ke_kota_km", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pesantren_id")
    )
    op.create_index("idx_pesantren_fasilitas_pesantren_id", "pesantren_fasilitas", ["pesantren_id"])
    
    # Create pesantren_pendidikan table
    op.create_table(
        "pesantren_pendidikan",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("jenjang_pendidikan", sa.String(), nullable=True),
        sa.Column("kurikulum", sa.String(), nullable=True),
        sa.Column("akreditasi", sa.String(), nullable=True),
        sa.Column("jumlah_guru_tetap", sa.Integer(), nullable=True),
        sa.Column("jumlah_guru_tidak_tetap", sa.Integer(), nullable=True),
        sa.Column("guru_s1_keatas", sa.Integer(), nullable=True),
        sa.Column("prestasi_akademik", sa.String(), nullable=True),
        sa.Column("prestasi_non_akademik", sa.String(), nullable=True),
        sa.Column("program_unggulan", sa.String(), nullable=True),
        sa.Column("metode_pembayaran", sa.String(), nullable=True),
        sa.Column("biaya_bulanan_min", sa.Integer(), nullable=True),
        sa.Column("biaya_bulanan_max", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pesantren_id")
    )
    op.create_index("idx_pesantren_pendidikan_pesantren_id", "pesantren_pendidikan", ["pesantren_id"])


def downgrade() -> None:
    """Drop all pesantren tables."""
    op.drop_index("idx_pesantren_pendidikan_pesantren_id", table_name="pesantren_pendidikan")
    op.drop_table("pesantren_pendidikan")
    
    op.drop_index("idx_pesantren_fasilitas_pesantren_id", table_name="pesantren_fasilitas")
    op.drop_table("pesantren_fasilitas")
    
    op.drop_index("idx_pesantren_fisik_pesantren_id", table_name="pesantren_fisik")
    op.drop_table("pesantren_fisik")
    
    op.drop_index("idx_pondok_pesantren_kabupaten", table_name="pondok_pesantren")
    op.drop_index("idx_pondok_pesantren_nama", table_name="pondok_pesantren")
    op.drop_table("pondok_pesantren")
