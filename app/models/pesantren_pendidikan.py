from sqlalchemy import Enum, Float, Integer, TIMESTAMP, func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import UUIDBase
from app.models.enum import (
    JenjangPendidikanEnum, KurikulumEnum, AkreditasiEnum, 
    PrestasiEnum
)

class PesantrenPendidikan(UUIDBase):
    __tablename__ = "pesantren_pendidikan"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    # Jenjang dan kurikulum
    jenjang_pendidikan = mapped_column(
        Enum(JenjangPendidikanEnum, name="jenjang_pendidikan_enum"), nullable=True
    )
    kurikulum = mapped_column(Enum(KurikulumEnum, name="kurikulum_enum"), nullable=True)
    akreditasi = mapped_column(Enum(AkreditasiEnum, name="akreditasi_enum"), nullable=True)

    # Guru
    jumlah_guru_tetap: Mapped[int] = mapped_column(Integer, nullable=True)
    jumlah_guru_tidak_tetap: Mapped[int] = mapped_column(Integer, nullable=True)
    guru_s1_keatas: Mapped[int] = mapped_column(Integer, nullable=True)
    persen_guru_bersertifikat: Mapped[int] = mapped_column(Integer, nullable=True)
    rasio_guru_santri: Mapped[float] = mapped_column(Float, nullable=True)

    # Prestasi dan program
    prestasi_akademik = mapped_column(String, nullable=True)
    prestasi_non_akademik = mapped_column(String, nullable=True)
    prestasi_santri = mapped_column(Enum(PrestasiEnum, name="prestasi_enum"), nullable=True)
    program_unggulan = mapped_column(String, nullable=True)

    # Fasilitas dan pembayaran
    fasilitas_mengajar = mapped_column(String, nullable=True)
    metode_pembayaran = mapped_column(String, nullable=True)
    biaya_bulanan_min: Mapped[int] = mapped_column(Integer, nullable=True)
    biaya_bulanan_max: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="pendidikan")
