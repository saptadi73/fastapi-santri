from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase

class SantriRumah(UUIDBase):
    __tablename__ = "santri_rumah"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status_rumah = Column(
        Enum("milik_sendiri", "kontrak", "menumpang", name="status_rumah_enum"),
        nullable=False
    )

    jenis_lantai = Column(
        Enum("tanah", "semen", "keramik", name="jenis_lantai_enum"),
        nullable=False
    )

    jenis_dinding = Column(
        Enum("bambu", "kayu", "tembok", name="jenis_dinding_enum"),
        nullable=False
    )

    jenis_atap = Column(
        Enum("rumbia", "seng", "genteng", "beton", name="jenis_atap_enum"),
        nullable=False
    )

    akses_air_bersih = Column(
        Enum("layak", "tidak_layak", name="akses_air_enum"),
        nullable=False
    )

    # 🔥 FINAL VERSION
    daya_listrik_va = Column(
        Enum(
            "450",
            "900",
            "1300",
            "2200",
            "3500",
            "5500",
            name="daya_listrik_va_enum"
        ),
        nullable=True
    )
