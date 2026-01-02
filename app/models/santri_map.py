"""Model for Santri GIS Mapping."""
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import UUIDBase


class SantriMap(UUIDBase):
    """Model for santri mapping in GIS.
    
    This table is automatically populated/updated when santri scoring is calculated.
    Used specifically for PostGIS mapping and visualization.
    """
    __tablename__ = "santri_map"
    
    # Foreign key to santri_pribadi
    santri_id = Column(
        UUID(as_uuid=True),
        ForeignKey("santri_pribadi.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Basic info for display
    nama = Column(String(150), nullable=False, index=True)
    
    # Latest score info
    skor_terakhir = Column(Integer, nullable=False, default=0)
    kategori_kemiskinan = Column(String(50), nullable=False, default="Tidak Miskin")
    
    # GIS location (POINT geometry with SRID 4326)
    lokasi = Column(
        Geometry("POINT", srid=4326),
        nullable=True,
        index=True
    )
    
    # Pesantren info for filtering
    pesantren_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pondok_pesantren.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationships
    santri = relationship("SantriPribadi", foreign_keys=[santri_id])
    pesantren = relationship(
        "PondokPesantren",
        foreign_keys=[pesantren_id],
        back_populates="santri_gis",
    )
    
    # Spatial index for geometry column
    __table_args__ = (
        Index('idx_santri_map_lokasi', 'lokasi', postgresql_using='gist'),
        Index('idx_santri_map_kategori', 'kategori_kemiskinan'),
    )
