"""Schemas for santri bansos API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class SantriBansosBase(BaseModel):
    """Base schema for santri bansos."""
    pkh: bool = Field(False, description="Penerima Program Keluarga Harapan")
    bpnt: bool = Field(False, description="Bantuan Pangan Non Tunai")
    pip: bool = Field(False, description="Program Indonesia Pintar")
    kis_pbi: bool = Field(False, description="Kartu Indonesia Sehat Penerima Bantuan Iuran")
    blt_desa: bool = Field(False, description="Bantuan Langsung Tunai Desa")
    bantuan_lainnya: Optional[str] = Field(None, description="Bantuan lainnya yang diterima")


class SantriBansosCreate(SantriBansosBase):
    """Schema for creating santri bansos."""
    santri_id: UUID = Field(..., description="ID Santri Pribadi")


class SantriBansosUpdate(BaseModel):
    """Schema for updating santri bansos."""
    pkh: Optional[bool] = None
    bpnt: Optional[bool] = None
    pip: Optional[bool] = None
    kis_pbi: Optional[bool] = None
    blt_desa: Optional[bool] = None
    bantuan_lainnya: Optional[str] = None


class SantriBansosResponse(SantriBansosBase):
    """Response schema for santri bansos."""
    id: UUID
    santri_id: UUID
    
    class Config:
        from_attributes = True
