"""Schemas for pesantren skor API."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenSkorBase(BaseModel):
    """Base schema for pesantren skor."""
    pesantren_id: UUID
    skor_kelayakan_fisik: int
    skor_air_sanitasi: int
    skor_fasilitas_pendukung: int
    skor_mutu_pendidikan: int
    skor_total: int
    kategori_kelayakan: str
    metode: str
    version: str


class PesantrenSkorResponse(PesantrenSkorBase):
    """Response schema for pesantren skor."""
    id: UUID
    calculated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
