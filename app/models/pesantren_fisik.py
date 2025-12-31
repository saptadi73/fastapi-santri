from sqlalchemy import Enum, Integer, TIMESTAMP, func, ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.core.database import get_db
from app.models.base import UUIDBase
from app.models.enum import (
    JenisAtapEnum,
    JenisDindingEnum,
    JenisLantaiEnum,
    KondisiBangunanEnum,
    KualitasAirBersihEnum,
    SanitasiEnum,
    AirBersihEnum,
    KeamananBangunanEnum,
    StatusBangunanEnum,
    SumberAirEnum,
    FasilitasMCKEnum,
    SumberListrikEnum,
    KestabilanEnum
)

class PesantrenFisik(UUIDBase):
    __tablename__ = "pesantren_fisik"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    # Dimensi fisik
    luas_tanah: Mapped[float] = mapped_column(Float, nullable=True)
    luas_bangunan: Mapped[float] = mapped_column(Float, nullable=True)

    # Status dan kondisi bangunan
    kondisi_bangunan = mapped_column(
        Enum(KondisiBangunanEnum, name="kondisi_bangunan_enum"), nullable=False
    )
    status_bangunan = mapped_column(
        Enum(StatusBangunanEnum, name="status_bangunan_enum"), nullable=True
    )
    rasio_kepadatan_kamar: Mapped[float] = mapped_column(Float, nullable=False)

    # Air dan sanitasi
    sanitasi = mapped_column(
        Enum(SanitasiEnum, name="sanitasi_enum"), nullable=False
    )
    air_bersih = mapped_column(
        Enum(AirBersihEnum, name="air_bersih_enum"), nullable=False
    )
    sumber_air = mapped_column(
        Enum(SumberAirEnum, name="sumber_air_enum"), nullable=True
    )
    kualitas_air_bersih = mapped_column(
        Enum(KualitasAirBersihEnum, name="kualitas_air_bersih_enum"), nullable=True
    )
    fasilitas_mck = mapped_column(
        Enum(FasilitasMCKEnum, name="fasilitas_mck_enum"), nullable=True
    )
    jumlah_mck: Mapped[int] = mapped_column(Integer, nullable=True)

    # Keamanan
    keamanan_bangunan = mapped_column(
        Enum(KeamananBangunanEnum, name="keamanan_bangunan_enum"), nullable=False
    )
    sistem_keamanan = mapped_column(String, nullable=True)

    # Material bangunan
    jenis_lantai = mapped_column(Enum(JenisLantaiEnum, name="jenis_lantai_enum"), nullable=False)
    jenis_atap = mapped_column(Enum(JenisAtapEnum, name="jenis_atap_enum"), nullable=False)
    jenis_dinding = mapped_column(Enum(JenisDindingEnum, name="jenis_dinding_enum"), nullable=False)

    # Listrik
    sumber_listrik = mapped_column(
        Enum(SumberListrikEnum, name="sumber_listrik_enum"), nullable=True
    )
    daya_listrik_va = mapped_column(String, nullable=True)
    kestabilan_listrik = mapped_column(
        Enum(KestabilanEnum, name="kestabilan_listrik_enum"), nullable=True
    )


    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="fisik")
