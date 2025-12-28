"""Schemas for santri kesehatan API."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class SantriKesehatanBase(BaseModel):
    """Base schema for santri kesehatan."""
    tinggi_badan: Optional[float] = Field(None, ge=0, description="Tinggi badan dalam cm")
    berat_badan: Optional[float] = Field(None, ge=0, description="Berat badan dalam kg")
    status_gizi: Optional[str] = Field(None, description="baik, kurang, atau lebih")
    riwayat_penyakit: Optional[str] = Field(None, description="Riwayat penyakit yang pernah diderita")
    alergi_obat: Optional[str] = Field(None, description="Alergi obat-obatan")
    kebutuhan_khusus: Optional[str] = Field(None, description="Kebutuhan khusus kesehatan")
    
    @field_validator("status_gizi")
    @classmethod
    def validate_status_gizi(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["baik", "kurang", "lebih"]:
            raise ValueError("status_gizi must be 'baik', 'kurang', or 'lebih'")
        return v


class SantriKesehatanCreate(SantriKesehatanBase):
    """Schema for creating santri kesehatan."""
    santri_id: UUID = Field(..., description="ID Santri Pribadi")


class SantriKesehatanUpdate(BaseModel):
    """Schema for updating santri kesehatan."""
    tinggi_badan: Optional[float] = Field(None, ge=0)
    berat_badan: Optional[float] = Field(None, ge=0)
    status_gizi: Optional[str] = None
    riwayat_penyakit: Optional[str] = None
    alergi_obat: Optional[str] = None
    kebutuhan_khusus: Optional[str] = None
    
    @field_validator("status_gizi")
    @classmethod
    def validate_status_gizi(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["baik", "kurang", "lebih"]:
            raise ValueError("status_gizi must be 'baik', 'kurang', or 'lebih'")
        return v


class SantriKesehatanResponse(SantriKesehatanBase):
    """Response schema for santri kesehatan."""
    id: UUID
    santri_id: UUID
    
    class Config:
        from_attributes = True
