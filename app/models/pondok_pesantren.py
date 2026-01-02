from sqlalchemy import String, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
import uuid

from app.models.base import UUIDBase

class PondokPesantren(UUIDBase):
    __tablename__ = "pondok_pesantren"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    nama: Mapped[str] = mapped_column(String(200), nullable=False)
    nsp: Mapped[str | None] = mapped_column(String(50))
    tahun_berdiri: Mapped[int | None]

    jumlah_santri: Mapped[int | None]
    jumlah_guru: Mapped[int | None]

    alamat: Mapped[str | None]
    desa: Mapped[str | None]
    kecamatan: Mapped[str | None]
    kabupaten: Mapped[str | None]
    provinsi: Mapped[str | None]
    kode_pos: Mapped[str | None] = mapped_column(String(10))
    telepon: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(255))
    nama_kyai: Mapped[str | None] = mapped_column(String(200))

    lokasi = mapped_column(Geometry("POINT", srid=4326))
    foto_path: Mapped[str | None] = mapped_column(String(500))  # Main photo path

    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    fisik = relationship("PesantrenFisik", back_populates="pesantren", uselist=False)
    fasilitas = relationship("PesantrenFasilitas", back_populates="pesantren", uselist=False)
    pendidikan = relationship("PesantrenPendidikan", back_populates="pesantren", uselist=False)
    santri = relationship("SantriPribadi", back_populates="pesantren")
    # GIS mapping entries for santri
    santri_gis = relationship("SantriMap", back_populates="pesantren")
    skor = relationship("PesantrenSkor", back_populates="pesantren", uselist=False)
    foto_pesantren = relationship(
        "FotoPesantren",
        back_populates="pesantren",
        cascade="all, delete-orphan",
    )
