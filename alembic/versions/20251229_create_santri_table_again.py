"""create santri table to match app.santri.models

Revision ID: recreate_santri
Revises: add_missing_pendidikan_cols
Create Date: 2025-12-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = "recreate_santri"
down_revision: Union[str, Sequence[str], None] = "add_missing_pendidikan_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "santri",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ekonomi", sa.String(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("lokasi", geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.ForeignKeyConstraint(["pesantren_id"], ["pondok_pesantren.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade() -> None:
    op.drop_table("santri")
