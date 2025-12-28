"""API routes for pondok pesantren CRUD operations."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pondok_pesantren_service import PondokPesantrenService
from app.schemas.pondok_pesantren_schema import (
    PondokPesantrenResponse,
    PondokPesantrenCreate,
    PondokPesantrenUpdate
)

router = APIRouter(prefix="/pondok-pesantren", tags=["Pondok Pesantren"])


@router.get("")
def list_pesantren(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by nama or nsp"),
    provinsi: Optional[str] = Query(None),
    kabupaten: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get list of pondok pesantren with filters and pagination."""
    service = PondokPesantrenService(db)
    results, total = service.get_all(
        page=page,
        per_page=per_page,
        search=search,
        provinsi=provinsi,
        kabupaten=kabupaten
    )
    
    return {
        "data": results,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{pesantren_id}", response_model=PondokPesantrenResponse)
def get_pesantren(
    pesantren_id: UUID,
    db: Session = Depends(get_db)
):
    """Get pondok pesantren by ID."""
    service = PondokPesantrenService(db)
    pesantren = service.get_by_id(pesantren_id)
    
    if not pesantren:
        raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
    
    return pesantren


@router.post("", response_model=PondokPesantrenResponse, status_code=201)
def create_pesantren(
    data: PondokPesantrenCreate,
    db: Session = Depends(get_db)
):
    """Create new pondok pesantren."""
    service = PondokPesantrenService(db)
    return service.create(data)


@router.put("/{pesantren_id}", response_model=PondokPesantrenResponse)
def update_pesantren(
    pesantren_id: UUID,
    data: PondokPesantrenUpdate,
    db: Session = Depends(get_db)
):
    """Update pondok pesantren data."""
    service = PondokPesantrenService(db)
    pesantren = service.update(pesantren_id, data)
    
    if not pesantren:
        raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
    
    return pesantren


@router.delete("/{pesantren_id}", status_code=204)
def delete_pesantren(
    pesantren_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete pondok pesantren."""
    service = PondokPesantrenService(db)
    success = service.delete(pesantren_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")
