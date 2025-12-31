"""Schemas for Pesantren Map API."""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class PesantrenMapBase(BaseModel):
    """Base schema for pesantren map."""
    nama: str
    nsp: Optional[str] = None
    skor_terakhir: int
    kategori_kelayakan: str
    kabupaten: Optional[str] = None
    provinsi: Optional[str] = None
    jumlah_santri: Optional[int] = None


class PesantrenMapResponse(PesantrenMapBase):
    """Response schema for pesantren map."""
    id: UUID
    pesantren_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True


class PesantrenMapGeoJSON(BaseModel):
    """GeoJSON Feature schema for pesantren map."""
    type: str = "Feature"
    geometry: dict
    properties: dict
    
    class Config:
        from_attributes = True


class PesantrenMapCollection(BaseModel):
    """GeoJSON FeatureCollection for pesantren map."""
    type: str = "FeatureCollection"
    features: list[PesantrenMapGeoJSON]
    total: int
