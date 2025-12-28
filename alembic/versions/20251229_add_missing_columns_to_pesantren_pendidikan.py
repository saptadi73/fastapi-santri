"""add missing columns to pesantren_pendidikan to match model

Revision ID: add_missing_pendidikan_cols
Revises: add_missing_fasilitas_cols
Create Date: 2025-12-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_missing_pendidikan_cols"
down_revision: Union[str, Sequence[str], None] = "add_missing_fasilitas_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns expected by model but missing in initial schema (idempotent)
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS persen_guru_bersertifikat INTEGER")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS rasio_guru_santri DOUBLE PRECISION")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS akreditasi VARCHAR")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS prestasi_santri VARCHAR")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS fasilitas_mengajar VARCHAR")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT now()")
    op.execute("ALTER TABLE pesantren_pendidikan ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT now()")


def downgrade() -> None:
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS fasilitas_mengajar")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS prestasi_santri")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS akreditasi")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS rasio_guru_santri")
    op.execute("ALTER TABLE pesantren_pendidikan DROP COLUMN IF EXISTS persen_guru_bersertifikat")
