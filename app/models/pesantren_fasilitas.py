from sqlalchemy import Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import UUIDBase
from app.models.enum import KelayakanEnum, KetersediaanEnum, KestabilanEnum, FasilitasMCKEnum, FasilitasMengajarEnum, FasilitasKomunikasiEnum, FasilitasTransportasiEnum, AksesJalanEnum, MetodePembayaranEnum

class PesantrenFasilitas(UUIDBase):
    __tablename__ = "pesantren_fasilitas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pesantren_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        unique=True
    )

    asrama = mapped_column(Enum(KelayakanEnum, name="kelayakan_enum"), nullable=False)
    ruang_belajar = mapped_column(Enum(KelayakanEnum, name="kelayakan_enum"), nullable=False)

    perpustakaan = mapped_column(
        Enum(KetersediaanEnum, name="ketersediaan_enum"), nullable=False
    )
    laboratorium = mapped_column(
        Enum(KetersediaanEnum, name="ketersediaan_enum"), nullable=False
    )

    listrik = mapped_column(Enum(KestabilanEnum, name="kestabilan_enum"), nullable=False)
    internet = mapped_column(Enum(KestabilanEnum, name="kestabilan_enum"), nullable=False)

    fasilitas_mck = mapped_column(
        Enum(FasilitasMCKEnum, name="fasilitas_mck_enum"), nullable=False
    )

    fasilitas_mengajar = mapped_column(
        Enum(FasilitasMengajarEnum, name="fasilitas_mengajar_enum"), nullable=False
    )

    fasilitas_komunikasi = mapped_column(
        Enum(FasilitasKomunikasiEnum, name="fasilitas_komunikasi_enum"), nullable=False
    )

    fasilitas_transportasi = mapped_column(
        Enum(FasilitasTransportasiEnum, name="fasilitas_transportasi_enum"), nullable=False
    )

    akses_jalan = mapped_column(
        Enum(AksesJalanEnum, name="akses_jalan_enum"), nullable=False
    )

    metode_pembayaran = mapped_column(
        Enum(MetodePembayaranEnum, name="metode_pembayaran_enum"), nullable=False
    )

    created_at = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pesantren = relationship("PondokPesantren", back_populates="fasilitas")
