"""Routes for santri bansos endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_bansos_schema import (
    SantriBansosCreate,
    SantriBansosUpdate,
    SantriBansosResponse
)
from app.services.santri_bansos_service import SantriBansosService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-bansos", tags=["Santri Bansos"])


def get_service(db: Session = Depends(get_db)) -> SantriBansosService:
    """Dependency to get santri bansos service."""
    return SantriBansosService(db)


@router.get("", response_model=None)
async def get_all_bansos(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    santri_id: Optional[UUID] = Query(None, description="Filter by santri ID"),
    service: SantriBansosService = Depends(get_service)
):
    """Get all bansos records with pagination and filters."""
    bansos_list, total = service.get_all(
        page=page,
        per_page=per_page,
        santri_id=santri_id
    )
    
    return paginated_response(
        data=[SantriBansosResponse.model_validate(b).model_dump() for b in bansos_list],
        page=page,
        per_page=per_page,
        total=total,
        message="Data bansos berhasil diambil"
    )


@router.get("/{bansos_id}", response_model=None)
async def get_bansos_detail(
    bansos_id: UUID,
    service: SantriBansosService = Depends(get_service)
):
    """Get bansos detail by ID."""
    bansos = service.get_by_id(bansos_id)
    if not bansos:
        return error_response(
            message="Data bansos tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriBansosResponse.model_validate(bansos),
        message="Detail bansos berhasil diambil"
    )


@router.get("/santri/{santri_id}", response_model=None)
async def get_bansos_by_santri(
    santri_id: UUID,
    service: SantriBansosService = Depends(get_service)
):
    """Get bansos by santri ID."""
    bansos = service.get_by_santri_id(santri_id)
    if not bansos:
        return error_response(
            message="Data bansos untuk santri ini tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriBansosResponse.model_validate(bansos),
        message="Data bansos berhasil diambil"
    )


@router.post("", response_model=None)
async def create_bansos(
    data: SantriBansosCreate = Body(...),
    service: SantriBansosService = Depends(get_service)
):
    """Create new bansos record."""
    try:
        bansos = service.create(data)
        return success_response(
            data=SantriBansosResponse.model_validate(bansos),
            message="Data bansos berhasil ditambahkan",
            status_code=201
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        return error_response(
            message=f"Terjadi kesalahan: {str(e)}",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


@router.put("/{bansos_id}", response_model=None)
async def update_bansos(
    bansos_id: UUID,
    data: SantriBansosUpdate = Body(...),
    service: SantriBansosService = Depends(get_service)
):
    """Update bansos data (partial update)."""
    try:
        bansos = service.update(bansos_id, data)
        if not bansos:
            return error_response(
                message="Data bansos tidak ditemukan",
                status_code=404,
                error_code="NOT_FOUND"
            )
        
        return success_response(
            data=SantriBansosResponse.model_validate(bansos),
            message="Data bansos berhasil diupdate"
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        return error_response(
            message=f"Terjadi kesalahan: {str(e)}",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


@router.delete("/{bansos_id}", response_model=None)
async def delete_bansos(
    bansos_id: UUID,
    service: SantriBansosService = Depends(get_service)
):
    """Delete bansos record."""
    success = service.delete(bansos_id)
    if not success:
        return error_response(
            message="Data bansos tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    return success_response(
        data={"id": str(bansos_id)},
        message="Data bansos berhasil dihapus"
    )
