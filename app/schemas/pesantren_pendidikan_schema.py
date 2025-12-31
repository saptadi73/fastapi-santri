"""Schemas for pesantren pendidikan API."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from enum import Enum


class JenjangPendidikanEnum(str, Enum):
    """Enum for jenjang pendidikan values."""
    semua_ra_ma = "semua_ra_ma"
    pendidikan_dasar = "pendidikan_dasar"
    dasar_menengah_pertama = "dasar_menengah_pertama"
    dasar_menengah_atas = "dasar_menengah_atas"
    satu_jenjang = "satu_jenjang"


class KurikulumEnum(str, Enum):
    """Enum for kurikulum values."""
    terstandar = "terstandar"
    internal = "internal"
    tidak_jelas = "tidak_jelas"


class AkreditasiEnum(str, Enum):
    """Enum for akreditasi values."""
    a = "a"
    b = "b"
    c = "c"
    belum = "belum"


class PrestasiEnum(str, Enum):
    """Enum for prestasi values."""
    nasional = "nasional"
    regional = "regional"
    tidak_ada = "tidak_ada"


class PesantrenPendidikanBase(BaseModel):
    """Base schema for pesantren pendidikan."""
    pesantren_id: UUID = Field(..., description="ID pondok pesantren")
    
    # Jenjang dan kurikulum
    jenjang_pendidikan: Optional[JenjangPendidikanEnum] = Field(
        None, 
        description="semua_ra_ma/pendidikan_dasar/dasar_menengah_pertama/dasar_menengah_atas/satu_jenjang"
    )
    kurikulum: Optional[KurikulumEnum] = Field(None, description="terstandar/internal/tidak_jelas")
    akreditasi: Optional[AkreditasiEnum] = Field(None, description="a/b/c/belum")
    
    # Guru
    jumlah_guru_tetap: Optional[int] = Field(None, ge=0, description="Jumlah guru tetap")
    jumlah_guru_tidak_tetap: Optional[int] = Field(None, ge=0, description="Jumlah guru tidak tetap")
    guru_s1_keatas: Optional[int] = Field(None, ge=0, description="Jumlah guru dengan pendidikan S1 ke atas")
    persen_guru_bersertifikat: Optional[int] = Field(None, ge=0, le=100, description="Persentase guru bersertifikat")
    rasio_guru_santri: Optional[float] = Field(None, ge=0, description="Rasio guru terhadap santri")
    
    # Prestasi dan program
    prestasi_akademik: Optional[str] = Field(None, description="Contoh: nasional/regional/tidak_ada")
    prestasi_non_akademik: Optional[str] = Field(None, description="Contoh: nasional/regional/tidak_ada")
    prestasi_santri: Optional[PrestasiEnum] = Field(None, description="nasional/regional/tidak_ada")
    program_unggulan: Optional[str] = Field(None, description="Contoh: Tahfidz,Bahasa Arab")
    
    # Fasilitas dan pembayaran
    fasilitas_mengajar: Optional[str] = Field(None, description="projector/tv_monitor/whiteboard/papan_tulis")
    metode_pembayaran: Optional[str] = Field(None, description="tunai/non_tunai/campuran")
    biaya_bulanan_min: Optional[int] = Field(None, ge=0, description="Biaya bulanan minimum")
    biaya_bulanan_max: Optional[int] = Field(None, ge=0, description="Biaya bulanan maksimum")


class PesantrenPendidikanCreate(PesantrenPendidikanBase):
    """Schema for creating pesantren pendidikan."""
    pass


class PesantrenPendidikanUpdate(BaseModel):
    """Schema for updating pesantren pendidikan."""
    jenjang_pendidikan: Optional[JenjangPendidikanEnum] = None
    kurikulum: Optional[KurikulumEnum] = None
    akreditasi: Optional[AkreditasiEnum] = None
    jumlah_guru_tetap: Optional[int] = Field(None, ge=0)
    jumlah_guru_tidak_tetap: Optional[int] = Field(None, ge=0)
    guru_s1_keatas: Optional[int] = Field(None, ge=0)
    persen_guru_bersertifikat: Optional[int] = Field(None, ge=0, le=100)
    rasio_guru_santri: Optional[float] = Field(None, ge=0)
    prestasi_akademik: Optional[str] = None
    prestasi_non_akademik: Optional[str] = None
    prestasi_santri: Optional[PrestasiEnum] = None
    program_unggulan: Optional[str] = None
    fasilitas_mengajar: Optional[str] = None
    metode_pembayaran: Optional[str] = None
    biaya_bulanan_min: Optional[int] = Field(None, ge=0)
    biaya_bulanan_max: Optional[int] = Field(None, ge=0)


class PesantrenPendidikanResponse(PesantrenPendidikanBase):
    """Response schema for pesantren pendidikan."""
    id: UUID
    
    class Config:
        from_attributes = True
