"""Routes for santri asset endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_asset_schema import (
    SantriAssetCreate,
    SantriAssetUpdate,
    SantriAssetResponse,
    FotoAssetResponse
)
from app.services.santri_asset_service import SantriAssetService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-asset", tags=["Santri Asset"])


def get_service(db: Session = Depends(get_db)) -> SantriAssetService:
    """Dependency to get santri asset service."""
    return SantriAssetService(db)


@router.get("", response_model=None)
async def get_all_assets(
    santri_id: UUID = Query(..., description="Santri ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by jenis_aset"),
    jenis_aset: Optional[str] = Query(None, description="Filter by jenis_aset"),
    service: SantriAssetService = Depends(get_service)
):
    """Get all assets for a santri with pagination and filters."""
    try:
        asset_list, total = service.get_all(
            santri_id=santri_id,
            page=page,
            per_page=per_page,
            search=search,
            jenis_aset=jenis_aset
        )
        
        result = []
        for asset in asset_list:
            asset_dict = {
                "id": str(asset.id),
                "jenis_aset": asset.jenis_aset,
                "jumlah": asset.jumlah,
                "nilai_perkiraan": asset.nilai_perkiraan,
                "foto_count": len(asset.foto_asset) if asset.foto_asset else 0
            }
            result.append(asset_dict)
        
        return paginated_response(
            data=result,
            page=page,
            per_page=per_page,
            total=total
        )
    except Exception as e:
        return error_response(f"Failed to fetch assets: {str(e)}", error_code="INTERNAL_ERROR")


@router.get("/{asset_id}", response_model=None)
async def get_asset_detail(
    asset_id: UUID,
    service: SantriAssetService = Depends(get_service)
):
    """Get asset detail with photos."""
    try:
        asset = service.get_by_id(asset_id)
        
        if not asset:
            return error_response("Asset not found", error_code="NOT_FOUND")
        
        fotos = [
            {
                "id": str(foto.id),
                "asset_id": str(foto.asset_id),
                "nama_file": foto.nama_file,
                "url_photo": foto.url_photo
            }
            for foto in asset.foto_asset
        ]
        
        data = {
            "id": str(asset.id),
            "santri_id": str(asset.santri_id),
            "jenis_aset": asset.jenis_aset,
            "jumlah": asset.jumlah,
            "nilai_perkiraan": asset.nilai_perkiraan,
            "foto_asset": fotos
        }
        
        return success_response(data)
    except Exception as e:
        return error_response(f"Failed to fetch asset: {str(e)}", error_code="INTERNAL_ERROR")


@router.post("", response_model=None)
async def create_asset(
    santri_id: UUID = Form(...),
    jenis_aset: str = Form(...),
    jumlah: int = Form(default=1),
    nilai_perkiraan: Optional[int] = Form(None),
    fotos: List[UploadFile] = File(default=[]),
    service: SantriAssetService = Depends(get_service)
):
    """Create new asset with optional photos."""
    try:
        # Validate jenis_aset
        valid_types = ["motor", "mobil", "sepeda", "hp", "laptop", "lahan", "ternak", "alat_kerja", "lainnya"]
        if jenis_aset not in valid_types:
            return error_response(
                f"jenis_aset must be one of: {', '.join(valid_types)}",
                error_code="VALIDATION_ERROR"
            )
        
        # Validate jumlah
        if jumlah < 1:
            return error_response(
                "jumlah must be greater than 0",
                error_code="VALIDATION_ERROR"
            )
        
        data = SantriAssetCreate(
            santri_id=santri_id,
            jenis_aset=jenis_aset,
            jumlah=jumlah,
            nilai_perkiraan=nilai_perkiraan
        )
        
        asset = await service.create(santri_id, data, fotos if fotos else None)
        
        fotos_response = [
            {
                "id": str(f.id),
                "asset_id": str(f.asset_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in asset.foto_asset
        ]
        
        result = {
            "id": str(asset.id),
            "santri_id": str(asset.santri_id),
            "jenis_aset": asset.jenis_aset,
            "jumlah": asset.jumlah,
            "nilai_perkiraan": asset.nilai_perkiraan,
            "foto_asset": fotos_response
        }
        
        return success_response(result, status_code=201)
        
    except ValueError as e:
        return error_response(str(e), error_code="VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Failed to create asset: {str(e)}", error_code="UPLOAD_ERROR")


@router.put("/{asset_id}", response_model=None)
async def update_asset(
    asset_id: UUID,
    jenis_aset: Optional[str] = Form(None),
    jumlah: Optional[int] = Form(None),
    nilai_perkiraan: Optional[int] = Form(None),
    service: SantriAssetService = Depends(get_service)
):
    """Update asset by ID."""
    try:
        # Validate jenis_aset if provided
        if jenis_aset:
            valid_types = ["motor", "mobil", "sepeda", "hp", "laptop", "lahan", "ternak", "alat_kerja", "lainnya"]
            if jenis_aset not in valid_types:
                return error_response(
                    f"jenis_aset must be one of: {', '.join(valid_types)}",
                    error_code="VALIDATION_ERROR"
                )
        
        # Validate jumlah if provided
        if jumlah is not None and jumlah < 1:
            return error_response(
                "jumlah must be greater than 0",
                error_code="VALIDATION_ERROR"
            )
        
        data = SantriAssetUpdate(
            jenis_aset=jenis_aset,
            jumlah=jumlah,
            nilai_perkiraan=nilai_perkiraan
        )
        
        asset = await service.update(asset_id, data)
        
        if not asset:
            return error_response("Asset not found", error_code="NOT_FOUND")
        
        fotos_response = [
            {
                "id": str(f.id),
                "asset_id": str(f.asset_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in asset.foto_asset
        ]
        
        result = {
            "id": str(asset.id),
            "santri_id": str(asset.santri_id),
            "jenis_aset": asset.jenis_aset,
            "jumlah": asset.jumlah,
            "nilai_perkiraan": asset.nilai_perkiraan,
            "foto_asset": fotos_response
        }
        
        return success_response(result)
        
    except ValueError as e:
        return error_response(str(e), error_code="VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Failed to update asset: {str(e)}", error_code="INTERNAL_ERROR")


@router.delete("/{asset_id}", response_model=None)
async def delete_asset(
    asset_id: UUID,
    service: SantriAssetService = Depends(get_service)
):
    """Delete asset and related photos."""
    try:
        success = await service.delete(asset_id)
        
        if not success:
            return error_response("Asset not found", error_code="NOT_FOUND")
        
        return success_response({"message": "Asset deleted successfully"})
        
    except Exception as e:
        return error_response(f"Failed to delete asset: {str(e)}", error_code="INTERNAL_ERROR")


@router.post("/{asset_id}/photos", response_model=None)
async def add_asset_photos(
    asset_id: UUID,
    fotos: List[UploadFile] = File(...),
    service: SantriAssetService = Depends(get_service)
):
    """Add photos to existing asset."""
    try:
        if not fotos:
            return error_response("No files provided", error_code="VALIDATION_ERROR")
        
        fotos_obj = await service.add_photos(asset_id, fotos)
        
        result = [
            {
                "id": str(f.id),
                "asset_id": str(f.asset_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in fotos_obj
        ]
        
        return success_response(result, status_code=201)
        
    except Exception as e:
        return error_response(f"Failed to upload photos: {str(e)}", error_code="UPLOAD_ERROR")


@router.put("/photos/{foto_id}", response_model=None)
async def update_asset_photo(
    foto_id: UUID,
    foto: UploadFile = File(...),
    service: SantriAssetService = Depends(get_service)
):
    """Replace an asset photo with a new one."""
    try:
        updated_foto = await service.update_photo(foto_id, foto)
        
        if not updated_foto:
            return error_response("Photo not found", error_code="NOT_FOUND")
        
        result = {
            "id": str(updated_foto.id),
            "asset_id": str(updated_foto.asset_id),
            "nama_file": updated_foto.nama_file,
            "url_photo": updated_foto.url_photo
        }
        
        return success_response(result, message="Photo updated successfully")
        
    except Exception as e:
        return error_response(f"Failed to update photo: {str(e)}", error_code="UPLOAD_ERROR")


@router.delete("/photos/{foto_id}", response_model=None)
async def delete_asset_photo(
    foto_id: UUID,
    service: SantriAssetService = Depends(get_service)
):
    """Delete single asset photo."""
    try:
        success = await service.delete_photo(foto_id)
        
        if not success:
            return error_response("Photo not found", error_code="NOT_FOUND")
        
        return success_response({"message": "Photo deleted successfully"})
        
    except Exception as e:
        return error_response(f"Failed to delete photo: {str(e)}", error_code="INTERNAL_ERROR")
