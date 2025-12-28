"""add contact fields to pondok_pesantren

Revision ID: add_contact_fields_pesantren
Revises: add_foto_path
Create Date: 2025-12-28
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_contact_fields_pesantren'
down_revision = 'add_foto_path'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Columns may already exist from base creation; use IF NOT EXISTS to avoid duplicate errors
    op.execute("ALTER TABLE pondok_pesantren ADD COLUMN IF NOT EXISTS kode_pos VARCHAR(10)")
    op.execute("ALTER TABLE pondok_pesantren ADD COLUMN IF NOT EXISTS telepon VARCHAR(50)")
    op.execute("ALTER TABLE pondok_pesantren ADD COLUMN IF NOT EXISTS email VARCHAR(100)")
    op.execute("ALTER TABLE pondok_pesantren ADD COLUMN IF NOT EXISTS website VARCHAR(255)")
    op.execute("ALTER TABLE pondok_pesantren ADD COLUMN IF NOT EXISTS nama_kyai VARCHAR(200)")


def downgrade() -> None:
    op.execute("ALTER TABLE pondok_pesantren DROP COLUMN IF EXISTS nama_kyai")
    op.execute("ALTER TABLE pondok_pesantren DROP COLUMN IF EXISTS website")
    op.execute("ALTER TABLE pondok_pesantren DROP COLUMN IF EXISTS email")
    op.execute("ALTER TABLE pondok_pesantren DROP COLUMN IF EXISTS telepon")
    op.execute("ALTER TABLE pondok_pesantren DROP COLUMN IF EXISTS kode_pos")
