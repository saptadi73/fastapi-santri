"""Model for pesantren skor (scoring results)."""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class PesantrenSkor(UUIDBase):
    """Model for pesantren scoring results."""
    
    __tablename__ = "pesantren_skor"
    
    pesantren_id = Column(UUID(as_uuid=True), ForeignKey("pondok_pesantren.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Dimension scores
    skor_fisik = Column(Integer, nullable=False)
    skor_air_sanitasi = Column(Integer, nullable=False)
    skor_fasilitas_pendukung = Column(Integer, nullable=False)
    skor_mutu_pendidikan = Column(Integer, nullable=False)
    skor_fasilitas = Column(Integer, nullable=True)
    skor_pendidikan = Column(Integer, nullable=True)
    
    # Total score and category
    skor_total = Column(Integer, nullable=False)
    kategori_kelayakan = Column(String(30), nullable=False)  # sangat_layak, layak, cukup_layak, tidak_layak
    
    # Metadata
    metode = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    calculated_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    pesantren = relationship("PondokPesantren", back_populates="skor")
