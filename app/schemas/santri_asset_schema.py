"""Schemas for santri asset API."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class FotoAssetBase(BaseModel):
    """Base schema for asset photo."""
    nama_file: str
    url_photo: str


class FotoAssetResponse(FotoAssetBase):
    """Response schema for asset photo."""
    id: UUID
    asset_id: UUID
    
    class Config:
        from_attributes = True


class SantriAssetBase(BaseModel):
    """Base schema for santri asset."""
    santri_id: UUID = Field(..., description="ID santri")
    jenis_aset: str = Field(..., description="motor, mobil, sepeda, hp, laptop, lahan, ternak, alat_kerja, lainnya")
    jumlah: int = Field(default=1, ge=1)
    nilai_perkiraan: Optional[int] = Field(None, ge=0)
    
    @field_validator("jenis_aset")
    @classmethod
    def validate_jenis_aset(cls, v: str) -> str:
        valid_types = ["motor", "mobil", "sepeda", "hp", "laptop", "lahan", "ternak", "alat_kerja", "lainnya"]
        if v not in valid_types:
            raise ValueError(f"jenis_aset must be one of: {', '.join(valid_types)}")
        return v


class SantriAssetCreate(SantriAssetBase):
    """Schema for creating santri asset."""
    pass


class SantriAssetUpdate(BaseModel):
    """Schema for updating santri asset."""
    jenis_aset: Optional[str] = None
    jumlah: Optional[int] = Field(None, ge=1)
    nilai_perkiraan: Optional[int] = Field(None, ge=0)
    
    @field_validator("jenis_aset")
    @classmethod
    def validate_jenis_aset(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_types = ["motor", "mobil", "sepeda", "hp", "laptop", "lahan", "ternak", "alat_kerja", "lainnya"]
            if v not in valid_types:
                raise ValueError(f"jenis_aset must be one of: {', '.join(valid_types)}")
        return v


class SantriAssetResponse(SantriAssetBase):
    """Response schema for santri asset."""
    id: UUID
    foto_asset: List[FotoAssetResponse] = []
    
    class Config:
        from_attributes = True


class SantriAssetListResponse(BaseModel):
    """Response schema for santri asset list."""
    id: UUID
    jenis_aset: str
    jumlah: int
    nilai_perkiraan: Optional[int]
    foto_count: int = 0
    
    class Config:
        from_attributes = True
