"""add rasio_kepadatan_kamar column to pesantren_fisik

Revision ID: add_rasio_kamar
Revises: add_foto_pesantren
Create Date: 2025-12-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_rasio_kamar"
down_revision: Union[str, Sequence[str], None] = "add_foto_pesantren"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add column with default to satisfy existing rows
    op.add_column(
        "pesantren_fisik",
        sa.Column("rasio_kepadatan_kamar", sa.Float(), server_default=sa.text("0"), nullable=False)
    )
    # Remove the default if undesired after data backfill
    op.alter_column("pesantren_fisik", "rasio_kepadatan_kamar", server_default=None)


def downgrade() -> None:
    op.drop_column("pesantren_fisik", "rasio_kepadatan_kamar")
