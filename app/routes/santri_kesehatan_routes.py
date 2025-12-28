"""Routes for santri kesehatan endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_kesehatan_schema import (
    SantriKesehatanCreate,
    SantriKesehatanUpdate,
    SantriKesehatanResponse
)
from app.services.santri_kesehatan_service import SantriKesehatanService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-kesehatan", tags=["Santri Kesehatan"])


def get_service(db: Session = Depends(get_db)) -> SantriKesehatanService:
    """Dependency to get santri kesehatan service."""
    return SantriKesehatanService(db)


@router.get("", response_model=None)
async def get_all_kesehatan(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    santri_id: Optional[UUID] = Query(None, description="Filter by santri ID"),
    status_gizi: Optional[str] = Query(None, description="Filter by status gizi (baik/kurang/lebih)"),
    service: SantriKesehatanService = Depends(get_service)
):
    """Get all kesehatan records with pagination and filters."""
    kesehatan_list, total = service.get_all(
        page=page,
        per_page=per_page,
        santri_id=santri_id,
        status_gizi=status_gizi
    )
    
    return paginated_response(
        data=[SantriKesehatanResponse.model_validate(k).model_dump() for k in kesehatan_list],
        page=page,
        per_page=per_page,
        total=total,
        message="Data kesehatan berhasil diambil"
    )


@router.get("/{kesehatan_id}", response_model=None)
async def get_kesehatan_detail(
    kesehatan_id: UUID,
    service: SantriKesehatanService = Depends(get_service)
):
    """Get kesehatan detail by ID."""
    kesehatan = service.get_by_id(kesehatan_id)
    if not kesehatan:
        return error_response(
            message="Data kesehatan tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriKesehatanResponse.model_validate(kesehatan),
        message="Detail kesehatan berhasil diambil"
    )


@router.get("/santri/{santri_id}", response_model=None)
async def get_kesehatan_by_santri(
    santri_id: UUID,
    service: SantriKesehatanService = Depends(get_service)
):
    """Get kesehatan by santri ID."""
    kesehatan = service.get_by_santri_id(santri_id)
    if not kesehatan:
        return error_response(
            message="Data kesehatan untuk santri ini tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriKesehatanResponse.model_validate(kesehatan),
        message="Data kesehatan berhasil diambil"
    )


@router.post("", response_model=None)
async def create_kesehatan(
    data: SantriKesehatanCreate = Body(...),
    service: SantriKesehatanService = Depends(get_service)
):
    """Create new kesehatan record."""
    try:
        kesehatan = service.create(data)
        return success_response(
            data=SantriKesehatanResponse.model_validate(kesehatan),
            message="Data kesehatan berhasil ditambahkan",
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


@router.put("/{kesehatan_id}", response_model=None)
async def update_kesehatan(
    kesehatan_id: UUID,
    data: SantriKesehatanUpdate = Body(...),
    service: SantriKesehatanService = Depends(get_service)
):
    """Update kesehatan data (partial update)."""
    try:
        kesehatan = service.update(kesehatan_id, data)
        if not kesehatan:
            return error_response(
                message="Data kesehatan tidak ditemukan",
                status_code=404,
                error_code="NOT_FOUND"
            )
        
        return success_response(
            data=SantriKesehatanResponse.model_validate(kesehatan),
            message="Data kesehatan berhasil diupdate"
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


@router.delete("/{kesehatan_id}", response_model=None)
async def delete_kesehatan(
    kesehatan_id: UUID,
    service: SantriKesehatanService = Depends(get_service)
):
    """Delete kesehatan record."""
    success = service.delete(kesehatan_id)
    if not success:
        return error_response(
            message="Data kesehatan tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    return success_response(
        data={"id": str(kesehatan_id)},
        message="Data kesehatan berhasil dihapus"
    )
