from sqlalchemy import Enum, Float, Integer, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import UUIDBase
from app.models.enum import KurikulumEnum, AkreditasiEnum, PrestasiEnum, FasilitasMengajarEnum

class PesantrenPendidikan(UUIDBase):
    __tablename__ = "pesantren_pendidikan"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    kurikulum = mapped_column(Enum(KurikulumEnum, name="kurikulum_enum"), nullable=False)
    persen_guru_bersertifikat: Mapped[int] = mapped_column(Integer, nullable=False)
    rasio_guru_santri: Mapped[float] = mapped_column(Float, nullable=False)

    akreditasi = mapped_column(Enum(AkreditasiEnum, name="akreditasi_enum"), nullable=False)
    prestasi_santri = mapped_column(Enum(PrestasiEnum, name="prestasi_enum"), nullable=False)
    fasilitas_mengajar = mapped_column(
        Enum(FasilitasMengajarEnum, name="fasilitas_mengajar_enum"), nullable=False
    )

    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="pendidikan")
