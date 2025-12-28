from sqlalchemy import Column, Float, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase

class SantriKesehatan(UUIDBase):
    __tablename__ = "santri_kesehatan"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False
    )

    tinggi_badan = Column(Float)
    berat_badan = Column(Float)

    status_gizi = Column(
        Enum("baik", "kurang", "lebih", name="status_gizi_enum")
    )

    riwayat_penyakit = Column(String)
    alergi_obat = Column(String)
    kebutuhan_khusus = Column(String)