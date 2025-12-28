"""Schemas for santri scoring API."""
from uuid import UUID
from pydantic import BaseModel, Field

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

    class Config:
        from_attributes = True
