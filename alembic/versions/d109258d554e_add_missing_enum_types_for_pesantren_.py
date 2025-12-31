"""add missing enum types for pesantren_pendidikan

Revision ID: d109258d554e
Revises: 5955f6c5cc3d
Create Date: 2025-12-31 18:30:27.107851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd109258d554e'
down_revision: Union[str, Sequence[str], None] = '5955f6c5cc3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing enum types for pesantren_pendidikan table."""
    
    # Create kurikulum_enum
    op.execute("CREATE TYPE kurikulum_enum AS ENUM ('terstandar', 'internal', 'tidak_jelas')")
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN kurikulum TYPE kurikulum_enum 
        USING (
            CASE 
                WHEN kurikulum = '' OR kurikulum IS NULL THEN NULL
                ELSE kurikulum::kurikulum_enum
            END
        )
    """)
    
    # Create prestasi_enum
    op.execute("CREATE TYPE prestasi_enum AS ENUM ('nasional', 'regional', 'tidak_ada')")
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN prestasi_santri TYPE prestasi_enum 
        USING (
            CASE 
                WHEN prestasi_santri = '' OR prestasi_santri IS NULL THEN NULL
                ELSE prestasi_santri::prestasi_enum
            END
        )
    """)


def downgrade() -> None:
    """Revert enum types back to VARCHAR."""
    
    # Revert kurikulum
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN kurikulum TYPE VARCHAR 
        USING kurikulum::text
    """)
    op.execute("DROP TYPE kurikulum_enum")
    
    # Revert prestasi_santri
    op.execute("""
        ALTER TABLE pesantren_pendidikan 
        ALTER COLUMN prestasi_santri TYPE VARCHAR 
        USING prestasi_santri::text
    """)
    op.execute("DROP TYPE prestasi_enum")
