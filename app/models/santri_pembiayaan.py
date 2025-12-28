from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase

class SantriPembiayaan(UUIDBase):
    __tablename__ = "santri_pembiayaan"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False
    )

    biaya_per_bulan = Column(Integer)

    sumber_biaya = Column(
        Enum("orang_tua", "wali", "donatur", "beasiswa", name="sumber_biaya_enum")
    )

    nama_donatur = Column(String(150))
    jenis_beasiswa = Column(String(100))

    status_pembayaran = Column(
        Enum("lancar", "terlambat", "menunggak", name="status_pembayaran_enum")
    )

    tunggakan_bulan = Column(Integer, default=0)
    keterangan = Column(String)