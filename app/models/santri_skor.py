from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as _UUID
from app.models.base import UUIDBase


class SantriSkor(UUIDBase):
    __tablename__ = "santri_skor"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    skor_ekonomi = Column(Integer, nullable=False)
    skor_rumah = Column(Integer, nullable=False)
    skor_aset = Column(Integer, nullable=False)
    skor_pembiayaan = Column(Integer, nullable=False)
    skor_kesehatan = Column(Integer, nullable=False)
    skor_bansos = Column(Integer, nullable=False)

    skor_total = Column(Integer, nullable=False)
    kategori_kemiskinan = Column(String(30), nullable=False)

    metode = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)

    calculated_at = Column(DateTime, server_default=text("now()"))
