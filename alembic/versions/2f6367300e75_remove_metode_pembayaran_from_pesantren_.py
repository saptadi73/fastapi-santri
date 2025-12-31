"""remove metode_pembayaran from pesantren_fasilitas

Revision ID: 2f6367300e75
Revises: 52ac1f13215a
Create Date: 2025-12-31 19:33:09.900037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f6367300e75'
down_revision: Union[str, Sequence[str], None] = '52ac1f13215a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove metode_pembayaran (already exists in pesantren_pendidikan)."""
    op.execute("ALTER TABLE pesantren_fasilitas DROP COLUMN IF EXISTS metode_pembayaran")


def downgrade() -> None:
    """Restore metode_pembayaran column."""
    op.execute("ALTER TABLE pesantren_fasilitas ADD COLUMN IF NOT EXISTS metode_pembayaran VARCHAR")
