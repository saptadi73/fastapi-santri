"""Routes for santri rumah endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_rumah_schema import (
    SantriRumahCreate,
    SantriRumahUpdate,
    SantriRumahResponse
)
from app.services.santri_rumah_service import SantriRumahService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-rumah", tags=["Santri Rumah"])


def get_service(db: Session = Depends(get_db)) -> SantriRumahService:
    """Dependency to get santri rumah service."""
    return SantriRumahService(db)


@router.get("", response_model=None)
async def get_all_rumah(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    santri_id: Optional[UUID] = Query(None, description="Filter by santri ID"),
    pesantren_id: Optional[UUID] = Query(None, description="Filter by pondok pesantren ID"),
    service: SantriRumahService = Depends(get_service)
):
    """Get all rumah records with pagination and filters."""
    rumah_list, total = service.get_all(
        page=page,
        per_page=per_page,
        santri_id=santri_id,
        pesantren_id=pesantren_id
    )
    
    return paginated_response(
        data=[SantriRumahResponse.model_validate(r).model_dump() for r in rumah_list],
        page=page,
        per_page=per_page,
        total=total,
        message="Data rumah berhasil diambil"
    )


@router.get("/{rumah_id}", response_model=None)
async def get_rumah_detail(
    rumah_id: UUID,
    service: SantriRumahService = Depends(get_service)
):
    """Get rumah detail by ID."""
    rumah = service.get_by_id(rumah_id)
    if not rumah:
        return error_response(
            message="Data rumah tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriRumahResponse.model_validate(rumah),
        message="Detail rumah berhasil diambil"
    )


@router.get("/santri/{santri_id}", response_model=None)
async def get_rumah_by_santri(
    santri_id: UUID,
    service: SantriRumahService = Depends(get_service)
):
    """Get rumah by santri ID."""
    rumah = service.get_by_santri_id(santri_id)
    if not rumah:
        return error_response(
            message="Data rumah untuk santri ini tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriRumahResponse.model_validate(rumah),
        message="Data rumah berhasil diambil"
    )


@router.post("", response_model=None)
async def create_rumah(
    data: SantriRumahCreate = Body(...),
    service: SantriRumahService = Depends(get_service)
):
    """Create new rumah record."""
    try:
        rumah = service.create(data)
        return success_response(
            data=SantriRumahResponse.model_validate(rumah),
            message="Data rumah berhasil ditambahkan",
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


@router.put("/{rumah_id}", response_model=None)
async def update_rumah(
    rumah_id: UUID,
    data: SantriRumahUpdate = Body(...),
    service: SantriRumahService = Depends(get_service)
):
    """Update rumah data (partial update)."""
    try:
        rumah = service.update(rumah_id, data)
        if not rumah:
            return error_response(
                message="Data rumah tidak ditemukan",
                status_code=404,
                error_code="NOT_FOUND"
            )
        
        return success_response(
            data=SantriRumahResponse.model_validate(rumah),
            message="Data rumah berhasil diupdate"
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


@router.delete("/{rumah_id}", response_model=None)
async def delete_rumah(
    rumah_id: UUID,
    service: SantriRumahService = Depends(get_service)
):
    """Delete rumah by ID."""
    success = service.delete(rumah_id)
    if not success:
        return error_response(
            message="Data rumah tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    return success_response(
        data={"id": str(rumah_id)},
        message="Data rumah berhasil dihapus"
    )
