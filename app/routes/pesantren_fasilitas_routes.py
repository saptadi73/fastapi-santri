"""API routes for pesantren fasilitas CRUD operations."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pesantren_fasilitas_service import PesantrenFasilitasService
from app.schemas.pesantren_fasilitas_schema import (
    PesantrenFasilitasResponse,
    PesantrenFasilitasCreate,
    PesantrenFasilitasUpdate
)

router = APIRouter(prefix="/pesantren-fasilitas", tags=["Pesantren Fasilitas"])


@router.get("/pesantren/{pesantren_id}", response_model=PesantrenFasilitasResponse)
def get_fasilitas_by_pesantren(
    pesantren_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren fasilitas data by pesantren ID."""
    service = PesantrenFasilitasService(db)
    fasilitas = service.get_by_pesantren_id(pesantren_id)
    
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Data fasilitas tidak ditemukan")
    
    return fasilitas


@router.get("/{fasilitas_id}", response_model=PesantrenFasilitasResponse)
def get_fasilitas(
    fasilitas_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren fasilitas by ID."""
    service = PesantrenFasilitasService(db)
    fasilitas = service.get_by_id(fasilitas_id)
    
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Data fasilitas tidak ditemukan")
    
    return fasilitas


@router.post("", response_model=PesantrenFasilitasResponse, status_code=201)
def create_fasilitas(
    data: PesantrenFasilitasCreate,
    db: Session = Depends(get_db)
):
    """Create new pesantren fasilitas record."""
    service = PesantrenFasilitasService(db)
    return service.create(data)


@router.put("/{fasilitas_id}", response_model=PesantrenFasilitasResponse)
def update_fasilitas(
    fasilitas_id: UUID,
    data: PesantrenFasilitasUpdate,
    db: Session = Depends(get_db)
):
    """Update pesantren fasilitas data."""
    service = PesantrenFasilitasService(db)
    fasilitas = service.update(fasilitas_id, data)
    
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Data fasilitas tidak ditemukan")
    
    return fasilitas


@router.delete("/{fasilitas_id}", status_code=204)
def delete_fasilitas(
    fasilitas_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete pesantren fasilitas record."""
    service = PesantrenFasilitasService(db)
    success = service.delete(fasilitas_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Data fasilitas tidak ditemukan")
