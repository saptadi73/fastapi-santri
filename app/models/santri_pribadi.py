from sqlalchemy import Column, String, Date, Enum, Integer, text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import UUIDBase

class SantriPribadi(UUIDBase):
    __tablename__ = "santri_pribadi"

    nama = Column(String(150), nullable=False)
    nik = Column(String(16))
    no_kk = Column(String(16))

    tempat_lahir = Column(String(100))
    tanggal_lahir = Column(Date)

    jenis_kelamin = Column(
        Enum("L", "P", name="jenis_kelamin_enum"),
        nullable=False
    )

    status_tinggal = Column(
        Enum("mondok", "pp", "mukim", name="status_tinggal_enum")
    )

    lama_mondok_tahun = Column(Integer)

    provinsi = Column(String(100))
    kabupaten = Column(String(100))
    kecamatan = Column(String(100))
    desa = Column(String(100))

    lokasi = Column(
        Geometry("POINT", srid=4326)
    )
    
    # Relationships
    foto_santri = relationship("FotoSantri", back_populates="santri", cascade="all, delete-orphan")
