"""Schemas for santri rumah."""

from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


class FotoRumahResponse(BaseModel):
    """Schema for foto rumah response."""
    id: UUID
    rumah_id: UUID
    nama_file: str
    url_photo: str

    class Config:
        from_attributes = True


class SantriRumahCreate(BaseModel):
    """Schema for creating santri rumah."""
    santri_id: UUID
    status_rumah: str  # milik_sendiri, kontrak, menumpang
    jenis_lantai: str  # tanah, semen, keramik
    jenis_dinding: str  # bambu, kayu, tembok
    jenis_atap: str  # rumbia, seng, genteng, beton
    akses_air_bersih: str  # layak, tidak_layak
    daya_listrik_va: Optional[str] = None  # 450, 900, 1300, 2200, 3500, 5500


class SantriRumahUpdate(BaseModel):
    """Schema for updating santri rumah."""
    status_rumah: Optional[str] = None
    jenis_lantai: Optional[str] = None
    jenis_dinding: Optional[str] = None
    jenis_atap: Optional[str] = None
    akses_air_bersih: Optional[str] = None
    daya_listrik_va: Optional[str] = None


class SantriRumahResponse(BaseModel):
    """Schema for santri rumah response."""
    id: UUID
    santri_id: UUID
    status_rumah: str
    jenis_lantai: str
    jenis_dinding: str
    jenis_atap: str
    akses_air_bersih: str
    daya_listrik_va: Optional[str] = None
    foto_rumah: List[FotoRumahResponse] = []

    class Config:
        from_attributes = True
