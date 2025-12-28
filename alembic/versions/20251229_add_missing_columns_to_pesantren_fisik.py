"""add missing columns to pesantren_fisik to match model

Revision ID: add_missing_fisik_cols
Revises: add_rasio_kamar
Create Date: 2025-12-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_missing_fisik_cols"
down_revision: Union[str, Sequence[str], None] = "add_rasio_kamar"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns expected by model but missing in initial schema (idempotent)
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS sanitasi VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS air_bersih VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS kualitas_air_bersih VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS keamanan_bangunan VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS jenis_lantai VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS jenis_atap VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS jenis_dinding VARCHAR")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT now()")
    op.execute("ALTER TABLE pesantren_fisik ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT now()")


def downgrade() -> None:
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS updated_at")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS created_at")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS jenis_dinding")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS jenis_atap")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS jenis_lantai")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS keamanan_bangunan")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS kualitas_air_bersih")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS air_bersih")
    op.execute("ALTER TABLE pesantren_fisik DROP COLUMN IF EXISTS sanitasi")
