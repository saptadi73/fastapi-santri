"""Schemas for pesantren fisik API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenFisikBase(BaseModel):
    """Base schema for pesantren fisik."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    
    # Dimensi fisik
    luas_tanah: Optional[float] = Field(None, ge=0, description="Luas tanah dalam m²")
    luas_bangunan: Optional[float] = Field(None, ge=0, description="Luas bangunan dalam m²")
    
    # Status dan kondisi bangunan
    kondisi_bangunan: str = Field(..., description="permanen/semi_permanen/non_permanen")
    status_bangunan: Optional[str] = Field(None, description="milik_sendiri/wakaf/hibah/pinjam/sewa")
    rasio_kepadatan_kamar: float = Field(..., ge=0, description="Rasio santri per kamar")
    
    # Air dan sanitasi
    sanitasi: str = Field(..., description="layak/cukup/tidak_layak")
    air_bersih: str = Field(..., description="lancar/terbatas/tidak_tersedia")
    sumber_air: Optional[str] = Field(None, description="PDAM/sumur/berbagai_macam/hujan/sungai")
    kualitas_air_bersih: Optional[str] = Field(None, description="layak_minum/keruh/berbau/asin")
    fasilitas_mck: Optional[str] = Field(None, description="lengkap/cukup/kurang_lengkap/tidak_layak")
    jumlah_mck: Optional[int] = Field(None, ge=0, description="Jumlah MCK")
    
    # Keamanan
    keamanan_bangunan: str = Field(..., description="tinggi/standar/minim/tidak_aman")
    sistem_keamanan: Optional[str] = Field(None, description="Deskripsi sistem keamanan")
    
    # Material bangunan
    jenis_lantai: str = Field(..., description="marmer/keramik/beton/kayu/tanah")
    jenis_atap: str = Field(..., description="genteng_tanah_liat/metal/upvc/seng/asbes/ijuk")
    jenis_dinding: str = Field(..., description="tembok/papan/kayu/bambu/anyaman")
    
    # Listrik
    sumber_listrik: Optional[str] = Field(None, description="PLN/genset/listrik_tidak_ada/tenaga_surya")
    daya_listrik_va: Optional[str] = Field(None, description="Daya listrik dalam VA")
    kestabilan_listrik: Optional[str] = Field(None, description="stabil/tidak_stabil/tidak_ada")


class PesantrenFisikCreate(PesantrenFisikBase):
    """Schema for creating pesantren fisik."""
    pass


class PesantrenFisikUpdate(BaseModel):
    """Schema for updating pesantren fisik."""
    luas_tanah: Optional[float] = Field(None, ge=0)
    luas_bangunan: Optional[float] = Field(None, ge=0)
    kondisi_bangunan: Optional[str] = None
    status_bangunan: Optional[str] = None
    rasio_kepadatan_kamar: Optional[float] = Field(None, ge=0)
    sanitasi: Optional[str] = None
    air_bersih: Optional[str] = None
    sumber_air: Optional[str] = None
    kualitas_air_bersih: Optional[str] = None
    fasilitas_mck: Optional[str] = None
    jumlah_mck: Optional[int] = Field(None, ge=0)
    keamanan_bangunan: Optional[str] = None
    sistem_keamanan: Optional[str] = None
    jenis_lantai: Optional[str] = None
    jenis_atap: Optional[str] = None
    jenis_dinding: Optional[str] = None
    sumber_listrik: Optional[str] = None
    daya_listrik_va: Optional[str] = None
    kestabilan_listrik: Optional[str] = None


class PesantrenFisikResponse(PesantrenFisikBase):
    """Response schema for pesantren fisik."""
    id: UUID
    
    class Config:
        from_attributes = True
