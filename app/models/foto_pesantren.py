"""Model for pondok pesantren photos."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class FotoPesantren(UUIDBase):
    """Store additional photos for pondok pesantren."""

    __tablename__ = "foto_pesantren"

    pesantren_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        nullable=False,
    )
    nama_file = Column(String(255), nullable=False)
    url_photo = Column(String(500), nullable=False)

    # Relationships
    pesantren = relationship("PondokPesantren", back_populates="foto_pesantren")
