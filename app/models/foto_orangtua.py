"""Model for parent/guardian photos."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class FotoOrangtua(UUIDBase):
    """Model for parent/guardian photos."""
    
    __tablename__ = "foto_orangtua"
    
    orangtua_id = Column(UUID(as_uuid=True), ForeignKey("santri_orangtua.id", ondelete="CASCADE"), nullable=False)
    nama_file = Column(String(255), nullable=False)
    url_photo = Column(String(500), nullable=False)
    
    # Relationships
    orangtua = relationship("SantriOrangtua", back_populates="foto_orangtua")
