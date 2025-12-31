"""change akreditasi enum to lowercase

Revision ID: 5955f6c5cc3d
Revises: 0a5dbd9f8f3d
Create Date: 2025-12-31 18:21:37.237215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5955f6c5cc3d'
down_revision: Union[str, Sequence[str], None] = '0a5dbd9f8f3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create akreditasi_enum with lowercase values and update pesantren_pendidikan column."""
    
    # Step 1: Create the new enum type with lowercase values
    op.execute("CREATE TYPE akreditasi_enum AS ENUM ('a', 'b', 'c', 'belum')")
    
    # Step 2: Alter the akreditasi column to use the enum
    # Since akreditasi is currently VARCHAR, we need to convert existing data
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN akreditasi TYPE akreditasi_enum 
        USING (
            CASE LOWER(akreditasi)
                WHEN 'a' THEN 'a'::akreditasi_enum
                WHEN 'b' THEN 'b'::akreditasi_enum
                WHEN 'c' THEN 'c'::akreditasi_enum
                WHEN 'belum' THEN 'belum'::akreditasi_enum
                ELSE NULL
            END
        )
    """)


def downgrade() -> None:
    """Revert akreditasi column from enum back to VARCHAR."""
    
    # Step 1: Convert column back to VARCHAR
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN akreditasi TYPE VARCHAR 
        USING akreditasi::text
    """)
    
    # Step 2: Drop the enum type
    op.execute("DROP TYPE akreditasi_enum")
