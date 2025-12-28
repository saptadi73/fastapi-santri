"""add pesantren_skor table

Revision ID: 20251228_add_pesantren_skor
Revises: 20251228_add_pesantren_fk_to_santri
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "pesantren_skor"
down_revision: Union[str, Sequence[str], None] = "pesantren_fk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pesantren_skor",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),

        sa.Column("skor_kelayakan_fisik", sa.Integer(), nullable=False),
        sa.Column("skor_air_sanitasi", sa.Integer(), nullable=False),
        sa.Column("skor_fasilitas_pendukung", sa.Integer(), nullable=False),
        sa.Column("skor_mutu_pendidikan", sa.Integer(), nullable=False),

        sa.Column("skor_total", sa.Integer(), nullable=False),
        sa.Column("kategori_kelayakan", sa.String(length=30), nullable=False),

        sa.Column("metode", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),

        sa.Column("calculated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pesantren_id"),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("pesantren_skor")
