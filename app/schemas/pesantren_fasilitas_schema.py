"""Schemas for pesantren fasilitas API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenFasilitasBase(BaseModel):
    """Base schema for pesantren fasilitas."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    sumber_listrik: str = Field(..., description="PLN/tenaga_surya/genset/listrik_tidak_ada")
    kestabilan_listrik: Optional[str] = Field(None, description="stabil/tidak_stabil/tidak_ada")
    fasilitas_mengajar: Optional[str] = Field(None, description="projector/tv_monitor/whiteboard/papan_tulis")
    fasilitas_komunikasi: Optional[str] = Field(None, description="internet/telepon/pos")
    fasilitas_transportasi: Optional[str] = Field(None, description="bus/angkutan_umum/ojek/kendaraan_pribadi")
    akses_jalan: Optional[str] = Field(None, description="aspal/cor_block/kerikil/tanah")


class PesantrenFasilitasCreate(PesantrenFasilitasBase):
    """Schema for creating pesantren fasilitas."""
    pass


class PesantrenFasilitasUpdate(BaseModel):
    """Schema for updating pesantren fasilitas."""
    sumber_listrik: Optional[str] = None
    kestabilan_listrik: Optional[str] = None
    fasilitas_mengajar: Optional[str] = None
    fasilitas_komunikasi: Optional[str] = None
    fasilitas_transportasi: Optional[str] = None
    akses_jalan: Optional[str] = None


class PesantrenFasilitasResponse(PesantrenFasilitasBase):
    """Response schema for pesantren fasilitas."""
    id: UUID
    
    class Config:
        from_attributes = True
