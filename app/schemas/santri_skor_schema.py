"""Schemas for santri scoring API."""
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DimensiBreakdown(BaseModel):
    """Breakdown detail untuk satu dimensi scoring."""
    nama: str = Field(..., description="Nama dimensi (ekonomi, rumah, aset, dll)")
    skor: int = Field(..., description="Skor dimensi")
    skor_maks: int = Field(..., description="Skor maksimal dimensi")
    bobot: float = Field(..., description="Bobot dimensi dalam persen (0-100)")
    kontribusi: float = Field(..., description="Kontribusi ke total skor (skor * bobot)")
    interpretasi: str = Field(..., description="Interpretasi kondisi (Baik/Sedang/Buruk)")
    detail: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detail parameter yang berkontribusi")

class SkorBreakdown(BaseModel):
    """Breakdown lengkap scoring santri."""
    dimensi: List[DimensiBreakdown]
    skor_total: int
    kategori_kemiskinan: str
    interpretasi_kategori: str

class SantriSkorResponse(BaseModel):
    id: UUID
    santri_id: UUID

    skor_ekonomi: int
    skor_rumah: int
    skor_aset: int
    skor_pembiayaan: int
    skor_kesehatan: int
    skor_bansos: int

    skor_total: int
    kategori_kemiskinan: str

    metode: str
    version: str
    
    breakdown: Optional[SkorBreakdown] = Field(default=None, description="Detail breakdown scoring")

    class Config:
        from_attributes = True
