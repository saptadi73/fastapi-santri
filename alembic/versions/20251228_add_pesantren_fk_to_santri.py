"""add pesantren_id FK to santri and santri_pribadi

Revision ID: 20251228_add_pesantren_fk_to_santri
Revises: 20251228_add_santri_skor
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "pesantren_fk"
down_revision: Union[str, Sequence[str], None] = "create_pesantren"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # santri_pribadi: add column + FK
    op.add_column(
        "santri_pribadi",
        sa.Column("pesantren_id", sa.UUID(as_uuid=True), nullable=True)  # nullable for existing records
    )
    op.create_foreign_key(
        "fk_santri_pribadi_pesantren",
        "santri_pribadi",
        "pondok_pesantren",
        ["pesantren_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    # Drop FKs first, then columns
    op.drop_constraint("fk_santri_pribadi_pesantren", "santri_pribadi", type_="foreignkey")
    op.drop_column("santri_pribadi", "pesantren_id")
