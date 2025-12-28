from sqlalchemy import Column, Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase

class SantriBansos(UUIDBase):
    __tablename__ = "santri_bansos"

    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False
    )

    pkh = Column(Boolean, default=False)
    bpnt = Column(Boolean, default=False)
    pip = Column(Boolean, default=False)
    kis_pbi = Column(Boolean, default=False)
    blt_desa = Column(Boolean, default=False)
    bantuan_lainnya = Column(String)