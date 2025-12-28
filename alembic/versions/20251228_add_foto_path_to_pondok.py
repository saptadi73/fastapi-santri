"""add foto_path to pondok_pesantren

Revision ID: add_foto_path
Revises: pesantren_skor
Create Date: 2025-12-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_foto_path'
down_revision = 'pesantren_skor'
branch_labels = None
depends_on = None


def upgrade():
    # Add foto_path column to pondok_pesantren table
    op.add_column('pondok_pesantren', sa.Column('foto_path', sa.String(500), nullable=True))


def downgrade():
    # Remove foto_path column from pondok_pesantren table
    op.drop_column('pondok_pesantren', 'foto_path')
