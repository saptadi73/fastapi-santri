from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "santri_pribadi",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("nama", sa.String(150), nullable=False),
        sa.Column("nik", sa.String(16)),
        sa.Column("no_kk", sa.String(16)),
        sa.Column("tempat_lahir", sa.String(100)),
        sa.Column("tanggal_lahir", sa.Date),
        sa.Column("jenis_kelamin", sa.Enum("L","P", name="jenis_kelamin_enum")),
        sa.Column("status_tinggal", sa.Enum("mondok","pp","mukim", name="status_tinggal_enum")),
        sa.Column("lama_mondok_tahun", sa.Integer),
        sa.Column("provinsi", sa.String(100)),
        sa.Column("kabupaten", sa.String(100)),
        sa.Column("kecamatan", sa.String(100)),
        sa.Column("desa", sa.String(100)),
        sa.Column("lokasi", Geometry("POINT", srid=4326))
    )
    
def downgrade():
    op.drop_table("santri_pribadi")
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
    op.execute('DROP TYPE IF EXISTS jenis_kelamin_enum')
    op.execute('DROP TYPE IF EXISTS status_tinggal_enum')