from sqlalchemy import Enum, TIMESTAMP, func, ForeignKey, Integer, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import UUIDBase
from app.models.enum import (
    KelayakanEnum, 
    KestabilanEnum, 
    FasilitasTransportasiEnum, 
    AksesJalanEnum
)

class PesantrenFasilitas(UUIDBase):
    __tablename__ = "pesantren_fasilitas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    # Ruang dan kapasitas
    jumlah_kamar: Mapped[int] = mapped_column(Integer, nullable=True)
    jumlah_ruang_kelas: Mapped[int] = mapped_column(Integer, nullable=True)
    jumlah_masjid: Mapped[int] = mapped_column(Integer, nullable=True)

    # Fasilitas utama (ketersediaan as boolean)
    perpustakaan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    laboratorium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    ruang_komputer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    koperasi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    kantin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    # Fasilitas spesifik (deskripsi)
    fasilitas_olahraga = mapped_column(String, nullable=True)
    fasilitas_kesehatan = mapped_column(String, nullable=True)
    fasilitas_mengajar = mapped_column(String, nullable=True)
    fasilitas_komunikasi = mapped_column(String, nullable=True)
    akses_transportasi = mapped_column(String, nullable=True)
    jarak_ke_kota_km: Mapped[float] = mapped_column(Float, nullable=True)

    # Infrastruktur (status/kondisi)
    asrama = mapped_column(Enum(KelayakanEnum, name="kelayakan_enum"), nullable=True)
    ruang_belajar = mapped_column(Enum(KelayakanEnum, name="kelayakan_enum"), nullable=True)
    internet = mapped_column(Enum(KestabilanEnum, name="kestabilan_enum"), nullable=True)

    # Enum-based fasilitas
    fasilitas_transportasi = mapped_column(
        Enum(FasilitasTransportasiEnum, name="fasilitas_transportasi_enum"), nullable=True
    )
    akses_jalan = mapped_column(
        Enum(AksesJalanEnum, name="akses_jalan_enum"), nullable=True
    )

    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="fasilitas")
