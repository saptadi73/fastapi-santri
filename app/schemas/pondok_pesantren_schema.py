"""Schemas for pondok pesantren API."""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class PondokPesantrenBase(BaseModel):
    """Base schema for pondok pesantren."""
    nama: str = Field(..., min_length=1, max_length=200, description="Nama pondok pesantren")
    nsp: Optional[str] = Field(None, max_length=50, description="Nomor Statistik Pesantren")
    tahun_berdiri: Optional[int] = Field(None, ge=1800, le=2100)
    jumlah_santri: Optional[int] = Field(None, ge=0)
    jumlah_guru: Optional[int] = Field(None, ge=0)
    alamat: Optional[str] = None
    desa: Optional[str] = None
    kecamatan: Optional[str] = None
    kabupaten: Optional[str] = None
    provinsi: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PondokPesantrenCreate(PondokPesantrenBase):
    """Schema for creating pondok pesantren."""
    pass


class PondokPesantrenUpdate(BaseModel):
    """Schema for updating pondok pesantren."""
    nama: Optional[str] = Field(None, min_length=1, max_length=200)
    nsp: Optional[str] = Field(None, max_length=50)
    tahun_berdiri: Optional[int] = Field(None, ge=1800, le=2100)
    jumlah_santri: Optional[int] = Field(None, ge=0)
    jumlah_guru: Optional[int] = Field(None, ge=0)
    alamat: Optional[str] = None
    desa: Optional[str] = None
    kecamatan: Optional[str] = None
    kabupaten: Optional[str] = None
    provinsi: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PondokPesantrenResponse(PondokPesantrenBase):
    """Response schema for pondok pesantren."""
    id: UUID
    
    class Config:
        from_attributes = True


class PondokPesantrenListResponse(BaseModel):
    """Response schema for pondok pesantren list."""
    id: UUID
    nama: str
    nsp: Optional[str]
    kabupaten: Optional[str]
    provinsi: Optional[str]
    jumlah_santri: Optional[int]
    jumlah_guru: Optional[int]
    
    class Config:
        from_attributes = True
