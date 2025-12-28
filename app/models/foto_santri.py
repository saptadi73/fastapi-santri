"""Model for santri photos."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class FotoSantri(UUIDBase):
    """Model for santri profile photos."""
    
    __tablename__ = "foto_santri"
    
    santri_id = Column(UUID(as_uuid=True), ForeignKey("santri_pribadi.id", ondelete="CASCADE"), nullable=False)
    nama_file = Column(String(255), nullable=False)
    url_photo = Column(String(500), nullable=False)
    
    # Relationships
    santri = relationship("SantriPribadi", back_populates="foto_santri")
