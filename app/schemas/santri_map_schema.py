"""Schemas for Santri Map API."""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class SantriMapBase(BaseModel):
    """Base schema for santri map."""
    nama: str
    skor_terakhir: int
    kategori_kemiskinan: str
    pesantren_id: Optional[UUID] = None


class SantriMapResponse(SantriMapBase):
    """Response schema for santri map."""
    id: UUID
    santri_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True


class SantriMapGeoJSON(BaseModel):
    """GeoJSON Feature schema for santri map."""
    type: str = "Feature"
    geometry: dict
    properties: dict
    
    class Config:
        from_attributes = True


class SantriMapCollection(BaseModel):
    """GeoJSON FeatureCollection for santri map."""
    type: str = "FeatureCollection"
    features: list[SantriMapGeoJSON]
    total: int
