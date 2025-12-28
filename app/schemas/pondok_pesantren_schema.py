"""Schemas for pondok pesantren API."""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID


class FotoPesantrenResponse(BaseModel):
    """Response schema for foto pesantren."""
    nama_file: str
    url_photo: str

    class Config:
        from_attributes = True


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
    kode_pos: Optional[str] = Field(None, max_length=10)
    telepon: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    nama_kyai: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    foto_path: Optional[str] = Field(None, max_length=500, description="Path to main photo")


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
    kode_pos: Optional[str] = Field(None, max_length=10)
    telepon: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    nama_kyai: Optional[str] = Field(None, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    foto_path: Optional[str] = Field(None, max_length=500)


class PondokPesantrenResponse(PondokPesantrenBase):
    """Response schema for pondok pesantren."""
    id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    foto_pesantren: list["FotoPesantrenResponse"] = []
    
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
    nama_kyai: Optional[str]
    tahun_berdiri: Optional[int]
    
    class Config:
        from_attributes = True


class PondokPesantrenDropdownResponse(BaseModel):
    """Response schema for pondok pesantren dropdown."""
    id: UUID
    nama: str
    nsp: Optional[str]
    kabupaten: Optional[str]
    provinsi: Optional[str]
    
    class Config:
        from_attributes = True


class PaginatedPesantrenResponse(BaseModel):
    """Response schema for paginated pondok pesantren list."""
    data: list[PondokPesantrenListResponse]
    total: int
    page: int
    per_page: int


# Resolve forward references for Pydantic v2
PondokPesantrenResponse.model_rebuild()
