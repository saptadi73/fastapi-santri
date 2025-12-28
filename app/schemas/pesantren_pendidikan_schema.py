"""Schemas for pesantren pendidikan API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenPendidikanBase(BaseModel):
    """Base schema for pesantren pendidikan."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    kurikulum: str = Field(..., description="terstandar/internal/tidak_jelas")
    persen_guru_bersertifikat: int = Field(..., ge=0, le=100, description="Persentase guru bersertifikat")
    rasio_guru_santri: float = Field(..., ge=0, description="Rasio guru terhadap santri")
    akreditasi: str = Field(..., description="A/B/C/belum")
    prestasi_santri: Optional[str] = Field(None, description="nasional/regional/tidak_ada")
    fasilitas_mengajar: Optional[str] = Field(None, description="projector/tv_monitor/whiteboard/papan_tulis")
    metode_pembayaran: Optional[str] = Field(None, description="non_tunai/campuran/tunai")


class PesantrenPendidikanCreate(PesantrenPendidikanBase):
    """Schema for creating pesantren pendidikan."""
    pass


class PesantrenPendidikanUpdate(BaseModel):
    """Schema for updating pesantren pendidikan."""
    kurikulum: Optional[str] = None
    persen_guru_bersertifikat: Optional[int] = Field(None, ge=0, le=100)
    rasio_guru_santri: Optional[float] = Field(None, ge=0)
    akreditasi: Optional[str] = None
    prestasi_santri: Optional[str] = None
    fasilitas_mengajar: Optional[str] = None
    metode_pembayaran: Optional[str] = None


class PesantrenPendidikanResponse(PesantrenPendidikanBase):
    """Response schema for pesantren pendidikan."""
    id: UUID
    
    class Config:
        from_attributes = True
