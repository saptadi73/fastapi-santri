"""remove duplicate fields from pesantren_fasilitas

Revision ID: 52ac1f13215a
Revises: d109258d554e
Create Date: 2025-12-31 19:27:24.556618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52ac1f13215a'
down_revision: Union[str, Sequence[str], None] = 'd109258d554e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove duplicate fields that already exist in pesantren_fisik."""
    # Drop fasilitas_mck (already in pesantren_fisik)
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS fasilitas_mck")
    
    # Drop listrik (covered by sumber_listrik/kestabilan_listrik in pesantren_fisik)
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS listrik")


def downgrade() -> None:
    """Restore removed columns."""
    # Restore as VARCHAR for flexibility (can be converted back to enum if needed)
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS fasilitas_mck VARCHAR")
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS listrik VARCHAR")
