"""Model for asset photos."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class FotoAsset(UUIDBase):
    """Model for asset photos."""
    
    __tablename__ = "foto_asset"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("santri_asset.id", ondelete="CASCADE"), nullable=False)
    nama_file = Column(String(255), nullable=False)
    url_photo = Column(String(500), nullable=False)
    
    # Relationships
    asset = relationship("SantriAsset", back_populates="foto_asset")
