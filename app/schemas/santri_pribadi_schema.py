"""Schemas for santri pribadi API."""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
class PondokSummary(BaseModel):
    id: UUID
    nama: str

    class Config:
        from_attributes = True


class FotoSantriBase(BaseModel):
    """Base schema for santri photo."""
    nama_file: str
    url_photo: str


class FotoSantriResponse(FotoSantriBase):
    """Response schema for santri photo."""
    id: UUID
    santri_id: UUID
    
    class Config:
        from_attributes = True


class SantriPribadiBase(BaseModel):
    """Base schema for santri pribadi."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren tempat santri terdaftar")
    nama: str = Field(..., min_length=1, max_length=150, description="Nama lengkap santri")
    nik: Optional[str] = Field(None, max_length=16, description="Nomor Induk Kependudukan")
    no_kk: Optional[str] = Field(None, max_length=16, description="Nomor Kartu Keluarga")
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: str = Field(..., description="L atau P")
    status_tinggal: Optional[str] = Field(None, description="mondok, pp, atau mukim")
    lama_mondok_tahun: Optional[int] = Field(None, ge=0)
    provinsi: Optional[str] = Field(None, max_length=100)
    kabupaten: Optional[str] = Field(None, max_length=100)
    kecamatan: Optional[str] = Field(None, max_length=100)
    desa: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    @field_validator("jenis_kelamin")
    @classmethod
    def validate_jenis_kelamin(cls, v: str) -> str:
        if v not in ["L", "P"]:
            raise ValueError("jenis_kelamin must be 'L' or 'P'")
        return v
    
    @field_validator("status_tinggal")
    @classmethod
    def validate_status_tinggal(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["mondok", "pp", "mukim"]:
            raise ValueError("status_tinggal must be 'mondok', 'pp', or 'mukim'")
        return v


class SantriPribadiCreate(SantriPribadiBase):
    """Schema for creating santri pribadi."""
    pass


class SantriPribadiUpdate(BaseModel):
    """Schema for updating santri pribadi."""
    pesantren_id: Optional[UUID] = Field(None, description="ID pondok pesantren")
    nama: Optional[str] = Field(None, min_length=1, max_length=150)
    nik: Optional[str] = Field(None, max_length=16)
    no_kk: Optional[str] = Field(None, max_length=16)
    tempat_lahir: Optional[str] = Field(None, max_length=100)
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None
    status_tinggal: Optional[str] = None
    lama_mondok_tahun: Optional[int] = Field(None, ge=0)
    provinsi: Optional[str] = Field(None, max_length=100)
    kabupaten: Optional[str] = Field(None, max_length=100)
    kecamatan: Optional[str] = Field(None, max_length=100)
    desa: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    @field_validator("jenis_kelamin")
    @classmethod
    def validate_jenis_kelamin(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["L", "P"]:
            raise ValueError("jenis_kelamin must be 'L' or 'P'")
        return v
    
    @field_validator("status_tinggal")
    @classmethod
    def validate_status_tinggal(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["mondok", "pp", "mukim"]:
            raise ValueError("status_tinggal must be 'mondok', 'pp', or 'mukim'")
        return v


class SantriPribadiResponse(SantriPribadiBase):
    """Response schema for santri pribadi."""
    id: UUID
    foto_santri: List[FotoSantriResponse] = []
    pesantren: Optional[PondokSummary] = None
    
    class Config:
        from_attributes = True


class SantriPribadiListResponse(BaseModel):
    """Response schema for santri pribadi list."""
    id: UUID
    nama: str
    nik: Optional[str]
    jenis_kelamin: str
    provinsi: Optional[str]
    kabupaten: Optional[str]
    foto_count: int = 0
    pesantren_id: Optional[UUID] = None
    pesantren_nama: Optional[str] = None
    
    class Config:
        from_attributes = True
