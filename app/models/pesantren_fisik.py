from sqlalchemy import Enum, Integer, TIMESTAMP, func, ForeignKey, Float
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
    KeamananBangunanEnum
)

class PesantrenFisik(UUIDBase):
    __tablename__ = "pesantren_fisik"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    kondisi_bangunan = mapped_column(
        Enum(KondisiBangunanEnum, name="kondisi_bangunan_enum"), nullable=False
    )
    rasio_kepadatan_kamar: Mapped[float] = mapped_column(Float, nullable=False)

    sanitasi = mapped_column(
        Enum(SanitasiEnum, name="sanitasi_enum"), nullable=False
    )
    air_bersih = mapped_column(
        Enum(AirBersihEnum, name="air_bersih_enum"), nullable=False
    )

    kualitas_air_bersih = mapped_column(
        Enum(KualitasAirBersihEnum, name="kualitas_air_bersih_enum"), nullable=False
    )
    keamanan_bangunan = mapped_column(
        Enum(KeamananBangunanEnum, name="keamanan_bangunan_enum"), nullable=False
    )

    jenis_lantai = mapped_column(Enum(JenisLantaiEnum, name="jenis_lantai_enum"), nullable=False)
    jenis_atap = mapped_column(Enum(JenisAtapEnum, name="jenis_atap_enum"), nullable=False)
    jenis_dinding = mapped_column(Enum(JenisDindingEnum, name="jenis_dinding_enum"), nullable=False)


    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="fisik")
