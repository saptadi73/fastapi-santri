from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase


class SantriOrangtua(UUIDBase):
    __tablename__ = "santri_orangtua"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False
    )

    nama = Column(String(150), nullable=False)
    nik = Column(String(16))

    hubungan = Column(
        Enum("ayah", "ibu", "wali", name="hubungan_enum"),
        nullable=False
    )

    pendidikan = Column(String(50))
    pekerjaan = Column(String(100))
    pendapatan_bulanan = Column(Integer)

    status_hidup = Column(
        Enum("hidup", "meninggal", name="status_hidup_enum")
    )
    kontak_telepon = Column(String(15))
    
    # Relationships
    foto_orangtua = relationship("FotoOrangtua", back_populates="orangtua", cascade="all, delete-orphan")