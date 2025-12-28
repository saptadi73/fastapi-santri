"""add missing columns to pesantren_fasilitas to match model

Revision ID: add_missing_fasilitas_cols
Revises: add_missing_fisik_cols
Create Date: 2025-12-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_missing_fasilitas_cols"
down_revision: Union[str, Sequence[str], None] = "add_missing_fisik_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns expected by model but missing in initial schema (idempotent)
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS asrama VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS ruang_belajar VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS perpustakaan VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS laboratorium VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS listrik VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS internet VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS fasilitas_mck VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS fasilitas_mengajar VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS fasilitas_komunikasi VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS fasilitas_transportasi VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS akses_jalan VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS metode_pembayaran VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT now()")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT now()")


def downgrade() -> None:
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS metode_pembayaran")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS akses_jalan")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS fasilitas_transportasi")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS fasilitas_komunikasi")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS fasilitas_mengajar")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS fasilitas_mck")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS internet")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS listrik")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS laboratorium")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS perpustakaan")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS ruang_belajar")
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS asrama")
