"""add foto_pesantren table for multiple photos

Revision ID: add_foto_pesantren
Revises: santri_skor_20251228
Create Date: 2025-12-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_foto_pesantren"
down_revision: Union[str, Sequence[str], None] = "add_contact_fields_pesantren"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create foto_pesantren table."""
    op.create_table(
        "foto_pesantren",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("nama_file", sa.String(length=255), nullable=False),
        sa.Column("url_photo", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_foto_pesantren_pesantren_id", "foto_pesantren", ["pesantren_id"])


def downgrade() -> None:
    """Drop foto_pesantren table."""
    op.drop_index("idx_foto_pesantren_pesantren_id", table_name="foto_pesantren")
    op.drop_table("foto_pesantren")
