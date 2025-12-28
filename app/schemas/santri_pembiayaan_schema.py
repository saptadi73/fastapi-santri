"""Schemas for santri pembiayaan API."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class SantriPembiayaanBase(BaseModel):
    """Base schema for santri pembiayaan."""
    biaya_per_bulan: Optional[int] = Field(None, ge=0, description="Biaya per bulan dalam rupiah")
    sumber_biaya: Optional[str] = Field(None, description="orang_tua, wali, donatur, atau beasiswa")
    nama_donatur: Optional[str] = Field(None, max_length=150, description="Nama donatur jika ada")
    jenis_beasiswa: Optional[str] = Field(None, max_length=100, description="Jenis beasiswa jika ada")
    status_pembayaran: Optional[str] = Field(None, description="lancar, terlambat, atau menunggak")
    tunggakan_bulan: int = Field(0, ge=0, description="Jumlah bulan tunggakan")
    keterangan: Optional[str] = Field(None, description="Keterangan tambahan")
    
    @field_validator("sumber_biaya")
    @classmethod
    def validate_sumber_biaya(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["orang_tua", "wali", "donatur", "beasiswa"]:
            raise ValueError("sumber_biaya must be 'orang_tua', 'wali', 'donatur', or 'beasiswa'")
        return v
    
    @field_validator("status_pembayaran")
    @classmethod
    def validate_status_pembayaran(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["lancar", "terlambat", "menunggak"]:
            raise ValueError("status_pembayaran must be 'lancar', 'terlambat', or 'menunggak'")
        return v


class SantriPembiayaanCreate(SantriPembiayaanBase):
    """Schema for creating santri pembiayaan."""
    santri_id: UUID = Field(..., description="ID Santri Pribadi")


class SantriPembiayaanUpdate(BaseModel):
    """Schema for updating santri pembiayaan."""
    biaya_per_bulan: Optional[int] = Field(None, ge=0)
    sumber_biaya: Optional[str] = None
    nama_donatur: Optional[str] = Field(None, max_length=150)
    jenis_beasiswa: Optional[str] = Field(None, max_length=100)
    status_pembayaran: Optional[str] = None
    tunggakan_bulan: Optional[int] = Field(None, ge=0)
    keterangan: Optional[str] = None
    
    @field_validator("sumber_biaya")
    @classmethod
    def validate_sumber_biaya(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["orang_tua", "wali", "donatur", "beasiswa"]:
            raise ValueError("sumber_biaya must be 'orang_tua', 'wali', 'donatur', or 'beasiswa'")
        return v
    
    @field_validator("status_pembayaran")
    @classmethod
    def validate_status_pembayaran(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["lancar", "terlambat", "menunggak"]:
            raise ValueError("status_pembayaran must be 'lancar', 'terlambat', or 'menunggak'")
        return v


class SantriPembiayaanResponse(SantriPembiayaanBase):
    """Response schema for santri pembiayaan."""
    id: UUID
    santri_id: UUID
    
    class Config:
        from_attributes = True
