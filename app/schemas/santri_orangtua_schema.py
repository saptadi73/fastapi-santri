"""Schemas for santri orangtua API."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class FotoOrangtuaBase(BaseModel):
    """Base schema for parent photo."""
    nama_file: str
    url_photo: str


class FotoOrangtuaResponse(FotoOrangtuaBase):
    """Response schema for parent photo."""
    id: UUID
    orangtua_id: UUID
    
    class Config:
        from_attributes = True


class SantriOrangtuaBase(BaseModel):
    """Base schema for santri orangtua."""
    santri_id: UUID = Field(..., description="ID santri")
    nama: str = Field(..., min_length=1, max_length=150, description="Nama lengkap orang tua")
    nik: Optional[str] = Field(None, max_length=16, description="Nomor Induk Kependudukan")
    hubungan: str = Field(..., description="ayah, ibu, atau wali")
    pendidikan: Optional[str] = Field(None, max_length=50)
    pekerjaan: Optional[str] = Field(None, max_length=100)
    pendapatan_bulanan: Optional[int] = Field(None, ge=0)
    status_hidup: Optional[str] = Field(None, description="hidup atau meninggal")
    kontak_telepon: Optional[str] = Field(None, max_length=15)
    
    @field_validator("hubungan")
    @classmethod
    def validate_hubungan(cls, v: str) -> str:
        if v not in ["ayah", "ibu", "wali"]:
            raise ValueError("hubungan must be 'ayah', 'ibu', or 'wali'")
        return v
    
    @field_validator("status_hidup")
    @classmethod
    def validate_status_hidup(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["hidup", "meninggal"]:
            raise ValueError("status_hidup must be 'hidup' or 'meninggal'")
        return v


class SantriOrangtuaCreate(SantriOrangtuaBase):
    """Schema for creating santri orangtua."""
    pass


class SantriOrangtuaUpdate(BaseModel):
    """Schema for updating santri orangtua."""
    nama: Optional[str] = Field(None, min_length=1, max_length=150)
    nik: Optional[str] = Field(None, max_length=16)
    hubungan: Optional[str] = None
    pendidikan: Optional[str] = Field(None, max_length=50)
    pekerjaan: Optional[str] = Field(None, max_length=100)
    pendapatan_bulanan: Optional[int] = Field(None, ge=0)
    status_hidup: Optional[str] = None
    kontak_telepon: Optional[str] = Field(None, max_length=15)
    
    @field_validator("hubungan")
    @classmethod
    def validate_hubungan(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["ayah", "ibu", "wali"]:
            raise ValueError("hubungan must be 'ayah', 'ibu', or 'wali'")
        return v
    
    @field_validator("status_hidup")
    @classmethod
    def validate_status_hidup(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["hidup", "meninggal"]:
            raise ValueError("status_hidup must be 'hidup' or 'meninggal'")
        return v


class SantriOrangtuaResponse(SantriOrangtuaBase):
    """Response schema for santri orangtua."""
    id: UUID
    foto_orangtua: List[FotoOrangtuaResponse] = []
    
    class Config:
        from_attributes = True


class SantriOrangtuaListResponse(BaseModel):
    """Response schema for santri orangtua list."""
    id: UUID
    nama: str
    hubungan: str
    pekerjaan: Optional[str]
    status_hidup: Optional[str]
    foto_count: int = 0
    
    class Config:
        from_attributes = True
