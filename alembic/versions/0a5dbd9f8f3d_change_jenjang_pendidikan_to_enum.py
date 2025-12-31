"""change_jenjang_pendidikan_to_enum

Revision ID: 0a5dbd9f8f3d
Revises: recreate_santri
Create Date: 2025-12-31 18:08:15.463535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a5dbd9f8f3d'
down_revision: Union[str, Sequence[str], None] = 'recreate_santri'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type
    op.execute("""
        CREATE TYPE jenjang_pendidikan_enum AS ENUM (
            'semua_ra_ma',
            'pendidikan_dasar',
            'dasar_menengah_pertama',
            'dasar_menengah_atas',
            'satu_jenjang'
        )
    """)
    
    # Alter column to use enum type
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN jenjang_pendidikan TYPE jenjang_pendidikan_enum 
        USING jenjang_pendidikan::jenjang_pendidikan_enum
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert column to varchar
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN jenjang_pendidikan TYPE VARCHAR 
        USING jenjang_pendidikan::text
    """)
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS jenjang_pendidikan_enum")
