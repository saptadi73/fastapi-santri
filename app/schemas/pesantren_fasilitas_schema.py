"""Schemas for pesantren fasilitas API."""

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class PesantrenFasilitasBase(BaseModel):
    """Base schema for pesantren fasilitas."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    
    # Ruang dan kapasitas
    jumlah_kamar: Optional[int] = Field(None, ge=0, description="Jumlah kamar")
    jumlah_ruang_kelas: Optional[int] = Field(None, ge=0, description="Jumlah ruang kelas")
    jumlah_masjid: Optional[int] = Field(None, ge=0, description="Jumlah masjid")
    
    # Fasilitas utama (ketersediaan)
    perpustakaan: Optional[bool] = Field(None, description="Ada/tidak ada perpustakaan")
    laboratorium: Optional[bool] = Field(None, description="Ada/tidak ada laboratorium")
    ruang_komputer: Optional[bool] = Field(None, description="Ada/tidak ada")
    koperasi: Optional[bool] = Field(None, description="Ada/tidak ada")
    kantin: Optional[bool] = Field(None, description="Ada/tidak ada")
    
    # Fasilitas spesifik (deskripsi)
    fasilitas_olahraga: Optional[str] = Field(None, description="Contoh: lapangan futsal, basket")
    fasilitas_kesehatan: Optional[str] = Field(None, description="Contoh: klinik, poliklinik")
    fasilitas_mengajar: Optional[str] = Field(None, description="Contoh: projector, whiteboard")
    fasilitas_komunikasi: Optional[str] = Field(None, description="Contoh: internet, telepon")
    akses_transportasi: Optional[str] = Field(None, description="Contoh: angkutan umum, bus")
    jarak_ke_kota_km: Optional[float] = Field(None, ge=0, description="Jarak ke kota dalam km")
    
    # Infrastruktur (status/kondisi)
    asrama: Optional[str] = Field(None, description="layak/cukup/tidak_layak")
    ruang_belajar: Optional[str] = Field(None, description="layak/cukup/tidak_layak")
    internet: Optional[str] = Field(None, description="stabil/tidak_stabil/tidak_ada")
    
    # Enum-based fasilitas
    fasilitas_transportasi: Optional[str] = Field(None, description="bus/angkutan_umum/ojek/kendaraan_pribadi")
    akses_jalan: Optional[str] = Field(None, description="aspal/cor_block/kerikil/tanah")


class PesantrenFasilitasCreate(PesantrenFasilitasBase):
    """Schema for creating pesantren fasilitas."""
    pass


class PesantrenFasilitasUpdate(BaseModel):
    """Schema for updating pesantren fasilitas."""
    jumlah_kamar: Optional[int] = Field(None, ge=0)
    jumlah_ruang_kelas: Optional[int] = Field(None, ge=0)
    jumlah_masjid: Optional[int] = Field(None, ge=0)
    perpustakaan: Optional[bool] = None
    laboratorium: Optional[bool] = None
    ruang_komputer: Optional[bool] = None
    koperasi: Optional[bool] = None
    kantin: Optional[bool] = None
    fasilitas_olahraga: Optional[str] = None
    fasilitas_kesehatan: Optional[str] = None
    fasilitas_mengajar: Optional[str] = None
    fasilitas_komunikasi: Optional[str] = None
    akses_transportasi: Optional[str] = None
    jarak_ke_kota_km: Optional[float] = Field(None, ge=0)
    asrama: Optional[str] = None
    ruang_belajar: Optional[str] = None
    internet: Optional[str] = None
    fasilitas_transportasi: Optional[str] = None
    akses_jalan: Optional[str] = None


class PesantrenFasilitasResponse(PesantrenFasilitasBase):
    """Response schema for pesantren fasilitas."""
    id: UUID
    
    class Config:
        from_attributes = True
