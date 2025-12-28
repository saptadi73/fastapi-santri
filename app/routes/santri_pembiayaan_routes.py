"""Routes for santri pembiayaan endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_pembiayaan_schema import (
    SantriPembiayaanCreate,
    SantriPembiayaanUpdate,
    SantriPembiayaanResponse
)
from app.services.santri_pembiayaan_service import SantriPembiayaanService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-pembiayaan", tags=["Santri Pembiayaan"])


def get_service(db: Session = Depends(get_db)) -> SantriPembiayaanService:
    """Dependency to get santri pembiayaan service."""
    return SantriPembiayaanService(db)


@router.get("", response_model=None)
async def get_all_pembiayaan(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    santri_id: Optional[UUID] = Query(None, description="Filter by santri ID"),
    sumber_biaya: Optional[str] = Query(None, description="Filter by sumber biaya"),
    status_pembayaran: Optional[str] = Query(None, description="Filter by status pembayaran"),
    service: SantriPembiayaanService = Depends(get_service)
):
    """Get all pembiayaan records with pagination and filters."""
    pembiayaan_list, total = service.get_all(
        page=page,
        per_page=per_page,
        santri_id=santri_id,
        sumber_biaya=sumber_biaya,
        status_pembayaran=status_pembayaran
    )
    
    return paginated_response(
        data=[SantriPembiayaanResponse.model_validate(p).model_dump() for p in pembiayaan_list],
        page=page,
        per_page=per_page,
        total=total,
        message="Data pembiayaan berhasil diambil"
    )


@router.get("/{pembiayaan_id}", response_model=None)
async def get_pembiayaan_detail(
    pembiayaan_id: UUID,
    service: SantriPembiayaanService = Depends(get_service)
):
    """Get pembiayaan detail by ID."""
    pembiayaan = service.get_by_id(pembiayaan_id)
    if not pembiayaan:
        return error_response(
            message="Data pembiayaan tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriPembiayaanResponse.model_validate(pembiayaan),
        message="Detail pembiayaan berhasil diambil"
    )


@router.get("/santri/{santri_id}", response_model=None)
async def get_pembiayaan_by_santri(
    santri_id: UUID,
    service: SantriPembiayaanService = Depends(get_service)
):
    """Get pembiayaan by santri ID."""
    pembiayaan = service.get_by_santri_id(santri_id)
    if not pembiayaan:
        return error_response(
            message="Data pembiayaan untuk santri ini tidak ditemukan",
            status_code=404
        )
    
    return success_response(
        data=SantriPembiayaanResponse.model_validate(pembiayaan),
        message="Data pembiayaan berhasil diambil"
    )


@router.post("", response_model=None)
async def create_pembiayaan(
    data: SantriPembiayaanCreate = Body(...),
    service: SantriPembiayaanService = Depends(get_service)
):
    """Create new pembiayaan record."""
    try:
        pembiayaan = service.create(data)
        return success_response(
            data=SantriPembiayaanResponse.model_validate(pembiayaan),
            message="Data pembiayaan berhasil ditambahkan",
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


@router.put("/{pembiayaan_id}", response_model=None)
async def update_pembiayaan(
    pembiayaan_id: UUID,
    data: SantriPembiayaanUpdate = Body(...),
    service: SantriPembiayaanService = Depends(get_service)
):
    """Update pembiayaan data (partial update)."""
    try:
        pembiayaan = service.update(pembiayaan_id, data)
        if not pembiayaan:
            return error_response(
                message="Data pembiayaan tidak ditemukan",
                status_code=404,
                error_code="NOT_FOUND"
            )
        
        return success_response(
            data=SantriPembiayaanResponse.model_validate(pembiayaan),
            message="Data pembiayaan berhasil diupdate"
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


@router.delete("/{pembiayaan_id}", response_model=None)
async def delete_pembiayaan(
    pembiayaan_id: UUID,
    service: SantriPembiayaanService = Depends(get_service)
):
    """Delete pembiayaan record."""
    success = service.delete(pembiayaan_id)
    if not success:
        return error_response(
            message="Data pembiayaan tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    return success_response(
        data={"id": str(pembiayaan_id)},
        message="Data pembiayaan berhasil dihapus"
    )
