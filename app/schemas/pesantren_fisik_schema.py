"""Schemas for pesantren fisik API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenFisikBase(BaseModel):
    """Base schema for pesantren fisik."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    kondisi_bangunan: str = Field(..., description="permanen/semi_permanen/non_permanen")
    status_bangunan: Optional[str] = Field(None, description="milik_sendiri/wakaf/hibah/pinjam/sewa")
    rasio_kepadatan_kamar: float = Field(..., ge=0, description="Rasio santri per kamar")
    sanitasi: str = Field(..., description="layak/cukup/tidak_layak")
    air_bersih: str = Field(..., description="lancar/terbatas/tidak_tersedia")
    sumber_air: Optional[str] = Field(None, description="PDAM/sumur/berbagai_macam/hujan/sungai")
    kualitas_air_bersih: Optional[str] = Field(None, description="layak_minum/keruh/berbau/asin")
    keamanan_bangunan: str = Field(..., description="tinggi/standar/minim/tidak_aman")
    jenis_lantai: str = Field(..., description="marmer/keramik/beton/kayu/tanah")
    jenis_atap: str = Field(..., description="genteng_tanah_liat/metal/upvc/seng/asbes/ijuk")
    jenis_dinding: str = Field(..., description="tembok/papan/kayu/bambu/anyaman")
    fasilitas_mck: Optional[str] = Field(None, description="lengkap/cukup/kurang_lengkap/tidak_layak")


class PesantrenFisikCreate(PesantrenFisikBase):
    """Schema for creating pesantren fisik."""
    pass


class PesantrenFisikUpdate(BaseModel):
    """Schema for updating pesantren fisik."""
    kondisi_bangunan: Optional[str] = None
    status_bangunan: Optional[str] = None
    rasio_kepadatan_kamar: Optional[float] = Field(None, ge=0)
    sanitasi: Optional[str] = None
    air_bersih: Optional[str] = None
    sumber_air: Optional[str] = None
    kualitas_air_bersih: Optional[str] = None
    keamanan_bangunan: Optional[str] = None
    jenis_lantai: Optional[str] = None
    jenis_atap: Optional[str] = None
    jenis_dinding: Optional[str] = None
    fasilitas_mck: Optional[str] = None


class PesantrenFisikResponse(PesantrenFisikBase):
    """Response schema for pesantren fisik."""
    id: UUID
    
    class Config:
        from_attributes = True
