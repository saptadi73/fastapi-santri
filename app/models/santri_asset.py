from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class SantriAsset(UUIDBase):
    __tablename__ = "santri_asset"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    jenis_aset = Column(
        Enum(
            "motor",
            "mobil",
            "sepeda",
            "hp",
            "laptop",
            "lahan",
            "ternak",
            "alat_kerja",
            "lainnya",
            name="jenis_aset_enum"
        ),
        nullable=False
    )

    jumlah = Column(Integer, nullable=False, default=1)

    nilai_perkiraan = Column(Integer, nullable=True)
    
    # Relationships
    foto_asset = relationship("FotoAsset", back_populates="asset", cascade="all, delete-orphan")
