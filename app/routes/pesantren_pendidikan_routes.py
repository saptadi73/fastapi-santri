"""API routes for pesantren pendidikan CRUD operations."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pesantren_pendidikan_service import PesantrenPendidikanService
from app.schemas.pesantren_pendidikan_schema import (
    PesantrenPendidikanResponse,
    PesantrenPendidikanCreate,
    PesantrenPendidikanUpdate
)

router = APIRouter(prefix="/pesantren-pendidikan", tags=["Pesantren Pendidikan"])


@router.get("/pesantren/{pesantren_id}", response_model=PesantrenPendidikanResponse)
def get_pendidikan_by_pesantren(
    pesantren_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren pendidikan data by pesantren ID."""
    service = PesantrenPendidikanService(db)
    pendidikan = service.get_by_pesantren_id(pesantren_id)
    
    if not pendidikan:
        raise HTTPException(status_code=404, detail="Data pendidikan tidak ditemukan")
    
    return pendidikan


@router.get("/{pendidikan_id}", response_model=PesantrenPendidikanResponse)
def get_pendidikan(
    pendidikan_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pesantren pendidikan by ID."""
    service = PesantrenPendidikanService(db)
    pendidikan = service.get_by_id(pendidikan_id)
    
    if not pendidikan:
        raise HTTPException(status_code=404, detail="Data pendidikan tidak ditemukan")
    
    return pendidikan


@router.post("", response_model=PesantrenPendidikanResponse, status_code=201)
def create_pendidikan(
    data: PesantrenPendidikanCreate,
    db: Session = Depends(get_db)
):
    """Create new pesantren pendidikan record."""
    service = PesantrenPendidikanService(db)
    return service.create(data)


@router.put("/{pendidikan_id}", response_model=PesantrenPendidikanResponse)
def update_pendidikan(
    pendidikan_id: UUID,
    data: PesantrenPendidikanUpdate,
    db: Session = Depends(get_db)
):
    """Update pesantren pendidikan data."""
    service = PesantrenPendidikanService(db)
    pendidikan = service.update(pendidikan_id, data)
    
    if not pendidikan:
        raise HTTPException(status_code=404, detail="Data pendidikan tidak ditemukan")
    
    return pendidikan


@router.delete("/{pendidikan_id}", status_code=204)
def delete_pendidikan(
    pendidikan_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete pesantren pendidikan record."""
    service = PesantrenPendidikanService(db)
    success = service.delete(pendidikan_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Data pendidikan tidak ditemukan")
