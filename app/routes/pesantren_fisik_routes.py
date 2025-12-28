"""API routes for pesantren fisik CRUD operations."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pesantren_fisik_service import PesantrenFisikService
from app.schemas.pesantren_fisik_schema import (
    PesantrenFisikResponse,
    PesantrenFisikCreate,
    PesantrenFisikUpdate
)

router = APIRouter(prefix="/pesantren-fisik", tags=["Pesantren Fisik"])


@router.get("/pesantren/{pesantren_id}", response_model=PesantrenFisikResponse)
def get_fisik_by_pesantren(
    pesantren_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren fisik data by pesantren ID."""
    service = PesantrenFisikService(db)
    fisik = service.get_by_pesantren_id(pesantren_id)
    
    if not fisik:
        raise HTTPException(status_code=404, detail="Data fisik tidak ditemukan")
    
    return fisik


@router.get("/{fisik_id}", response_model=PesantrenFisikResponse)
def get_fisik(
    fisik_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren fisik by ID."""
    service = PesantrenFisikService(db)
    fisik = service.get_by_id(fisik_id)
    
    if not fisik:
        raise HTTPException(status_code=404, detail="Data fisik tidak ditemukan")
    
    return fisik


@router.post("", response_model=PesantrenFisikResponse, status_code=201)
def create_fisik(
    data: PesantrenFisikCreate,
    db: Session = Depends(get_db)
):
    """Create new pesantren fisik record."""
    service = PesantrenFisikService(db)
    return service.create(data)


@router.put("/{fisik_id}", response_model=PesantrenFisikResponse)
def update_fisik(
    fisik_id: UUID,
    data: PesantrenFisikUpdate,
    db: Session = Depends(get_db)
):
    """Update pesantren fisik data."""
    service = PesantrenFisikService(db)
    fisik = service.update(fisik_id, data)
    
    if not fisik:
        raise HTTPException(status_code=404, detail="Data fisik tidak ditemukan")
    
    return fisik


@router.delete("/{fisik_id}", status_code=204)
def delete_fisik(
    fisik_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete pesantren fisik record."""
    service = PesantrenFisikService(db)
    success = service.delete(fisik_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Data fisik tidak ditemukan")
