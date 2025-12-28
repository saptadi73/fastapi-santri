from sqlalchemy import Column, String, Float, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base
from sqlalchemy.orm import relationship


class Santri(Base):
    __tablename__ = "santri"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    pesantren_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String, nullable=False)
    ekonomi = Column(String)  # miskin / rentan / cukup
    score = Column(Float)

    # GIS POINT (longitude, latitude)
    lokasi = Column(
        Geometry(geometry_type="POINT", srid=4326)
    )

    # Relationship
    pesantren = relationship("PondokPesantren", back_populates="santri_gis")
