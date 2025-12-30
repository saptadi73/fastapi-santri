"""Model for rumah photos."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class FotoRumah(UUIDBase):
    """Model for rumah photos."""
    
    __tablename__ = "foto_rumah"
    
    rumah_id = Column(UUID(as_uuid=True), ForeignKey("santri_rumah.id", ondelete="CASCADE"), nullable=False)
    nama_file = Column(String(255), nullable=False)
    url_photo = Column(String(500), nullable=False)
    
    # Relationships
    rumah = relationship("SantriRumah", back_populates="foto_rumah")
