"""add santri_skor table

Revision ID: 20251228_add_santri_skor
Revises: d1a2b3c4d5e6
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251228_add_santri_skor"
down_revision: Union[str, Sequence[str], None] = "a0c591c0b479"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "santri_skor",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("santri_id", sa.UUID(as_uuid=True), nullable=False),

        sa.Column("skor_ekonomi", sa.Integer(), nullable=False),
        sa.Column("skor_rumah", sa.Integer(), nullable=False),
        sa.Column("skor_aset", sa.Integer(), nullable=False),
        sa.Column("skor_pembiayaan", sa.Integer(), nullable=False),
        sa.Column("skor_kesehatan", sa.Integer(), nullable=False),
        sa.Column("skor_bansos", sa.Integer(), nullable=False),

        sa.Column("skor_total", sa.Integer(), nullable=False),
        sa.Column("kategori_kemiskinan", sa.String(length=30), nullable=False),

        sa.Column("metode", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),

        sa.Column("calculated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("santri_id"),
        sa.ForeignKeyConstraint(["santri_id"], ["santri_pribadi.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("santri_skor")
