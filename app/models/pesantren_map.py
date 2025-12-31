"""Model for Pesantren GIS Mapping."""
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import UUIDBase


class PesantrenMap(UUIDBase):
    """Model for pesantren mapping in GIS.
    
    This table is automatically populated/updated when pesantren scoring is calculated.
    Used specifically for PostGIS mapping and visualization.
    """
    __tablename__ = "pesantren_map"
    
    # Foreign key to pondok_pesantren
    pesantren_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pondok_pesantren.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Basic info for display
    nama = Column(String(200), nullable=False, index=True)
    nsp = Column(String(50), nullable=True)
    
    # Latest score info
    skor_terakhir = Column(Integer, nullable=False, default=0)
    kategori_kelayakan = Column(String(50), nullable=False, default="tidak_layak")
    
    # GIS location (POINT geometry with SRID 4326)
    lokasi = Column(
        Geometry("POINT", srid=4326),
        nullable=True,
        index=True
    )
    
    # Additional info for display
    kabupaten = Column(String(100), nullable=True, index=True)
    provinsi = Column(String(100), nullable=True, index=True)
    jumlah_santri = Column(Integer, nullable=True)
    
    # Relationships
    pesantren = relationship("PondokPesantren", foreign_keys=[pesantren_id])
    
    # Spatial index for geometry column
    __table_args__ = (
        Index('idx_pesantren_map_lokasi', 'lokasi', postgresql_using='gist'),
        Index('idx_pesantren_map_kategori', 'kategori_kelayakan'),
    )
