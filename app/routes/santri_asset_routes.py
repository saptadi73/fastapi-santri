"""Routes for santri asset endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query, Form, Request
import json
from collections import defaultdict
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
    santri_id: Optional[UUID] = Query(None, description="Santri ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by jenis_aset"),
    jenis_aset: Optional[str] = Query(None, description="Filter by jenis_aset"),
    pesantren_id: Optional[UUID] = Query(None, description="Filter by pondok pesantren ID"),
    service: SantriAssetService = Depends(get_service)
):
    """Get all assets for a santri with pagination and filters."""
    try:
        asset_list, total = service.get_all(
            santri_id=santri_id,
            page=page,
            per_page=per_page,
            search=search,
            jenis_aset=jenis_aset,
            pesantren_id=pesantren_id
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
    request: Request,
    santri_id: UUID = Form(...),
    jenis_aset: str = Form(...),
    jumlah: int = Form(1),
    nilai_perkiraan: Optional[int] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriAssetService = Depends(get_service)
):
    """Create new asset with optional photos (multipart/form-data)."""
    try:
        data = SantriAssetCreate(
            santri_id=santri_id,
            jenis_aset=jenis_aset,
            jumlah=jumlah if jumlah is not None else 1,
            nilai_perkiraan=nilai_perkiraan
        )

        # Support multiple possible file field names: fotos / foto_files / files / foto_asset
        if not fotos or (isinstance(fotos, list) and len(fotos) == 0):
            form = await request.form()
            collected: List[UploadFile] = []
            for key, val in form.multi_items():
                if isinstance(val, UploadFile) and key in {"fotos", "foto_files", "files", "foto_asset"}:
                    collected.append(val)
            fotos = collected if collected else None

        asset = await service.create(data.santri_id, data, fotos)
        
        result = {
            "id": str(asset.id),
            "santri_id": str(asset.santri_id),
            "jenis_aset": asset.jenis_aset,
            "jumlah": asset.jumlah,
            "nilai_perkiraan": asset.nilai_perkiraan,
            "foto_asset": [
                {
                    "id": str(f.id),
                    "asset_id": str(f.asset_id),
                    "nama_file": f.nama_file,
                    "url_photo": f.url_photo
                }
                for f in asset.foto_asset
            ]
        }
        
        return success_response(result, status_code=201)
        
    except Exception as e:
        return error_response(f"Failed to create asset: {str(e)}", error_code="INTERNAL_ERROR")


@router.put("/{asset_id}", response_model=None)
async def update_asset(
    request: Request,
    asset_id: UUID,
    jenis_aset: Optional[str] = Form(None),
    jumlah: Optional[int] = Form(None),
    nilai_perkiraan: Optional[int] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriAssetService = Depends(get_service)
):
    """Update asset by ID with optional new photos (multipart/form-data)."""
    try:
        data = SantriAssetUpdate(
            jenis_aset=jenis_aset,
            jumlah=jumlah,
            nilai_perkiraan=nilai_perkiraan
        )
        
        # Support multiple possible file field names: fotos / foto_files / files / foto_asset
        if not fotos or (isinstance(fotos, list) and len(fotos) == 0):
            form = await request.form()
            collected: List[UploadFile] = []
            for key, val in form.multi_items():
                if isinstance(val, UploadFile) and key in {"fotos", "foto_files", "files", "foto_asset"}:
                    collected.append(val)
            fotos = collected if collected else None
        
        asset = await service.update(asset_id, data, fotos)
        
        if not asset:
            return error_response("Asset not found", error_code="NOT_FOUND")
        
        result = {
            "id": str(asset.id),
            "santri_id": str(asset.santri_id),
            "jenis_aset": asset.jenis_aset,
            "jumlah": asset.jumlah,
            "nilai_perkiraan": asset.nilai_perkiraan,
            "foto_asset": [
                {
                    "id": str(f.id),
                    "asset_id": str(f.asset_id),
                    "nama_file": f.nama_file,
                    "url_photo": f.url_photo
                }
                for f in asset.foto_asset
            ]
        }
        
        return success_response(result)
        
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


@router.post("/bulk", response_model=None)
async def create_assets_bulk(
    request: Request,
    assets: str = Form(..., description="JSON array of assets to create"),
    service: SantriAssetService = Depends(get_service)
):
    """Bulk create assets with optional grouped photos per asset.
    
    Expects multipart/form-data with:
    - assets: JSON array of objects [{ santri_id, jenis_aset, jumlah, nilai_perkiraan }]
    - fotos_{index}: one or more files for the asset at that array index (e.g., fotos_0, fotos_1)
    """
    try:
        # Parse JSON payload
        try:
            assets_payload = json.loads(assets)
            if not isinstance(assets_payload, list):
                return error_response("assets must be a JSON array", error_code="VALIDATION_ERROR")
        except json.JSONDecodeError:
            return error_response("Invalid JSON in assets field", error_code="VALIDATION_ERROR")

        # Collect uploaded files grouped by index with flexible key names
        fotos_by_index = defaultdict(list)
        form = await request.form()
        # Accept prefixes: fotos_, foto_files_, files_, foto_asset_ (plus unsuffixed fallback to index 0)
        allowed_prefixes = ["fotos_", "foto_files_", "files_", "foto_asset_"]
        fallback_keys = {"fotos", "foto_files", "files", "foto_asset"}
        for key, val in form.multi_items():
            if not isinstance(val, UploadFile):
                continue
            matched = False
            for prefix in allowed_prefixes:
                if key.startswith(prefix):
                    try:
                        idx = int(key[len(prefix):])
                    except ValueError:
                        matched = True
                        break
                    fotos_by_index[idx].append(val)
                    matched = True
                    break
            if matched:
                continue
            if key in fallback_keys:
                fotos_by_index[0].append(val)

        created = []

        # Optional normalization for common UI value
        def normalize_jenis_aset(v: Optional[str]) -> Optional[str]:
            mapping = {"handphone": "hp"}
            return mapping.get(v, v) if v is not None else None

        # Validate and create each asset
        for i, item in enumerate(assets_payload):
            if not isinstance(item, dict):
                return error_response(f"assets[{i}] must be an object", error_code="VALIDATION_ERROR")

            # Normalize and construct schema
            item_data = {
                "santri_id": item.get("santri_id"),
                "jenis_aset": normalize_jenis_aset(item.get("jenis_aset")),
                "jumlah": item.get("jumlah", 1),
                "nilai_perkiraan": item.get("nilai_perkiraan")
            }

            try:
                data_obj = SantriAssetCreate(**item_data)
            except Exception as e:
                return error_response(f"assets[{i}] validation error: {str(e)}", error_code="VALIDATION_ERROR")

            fotos = fotos_by_index.get(i) or None
            asset = await service.create(data_obj.santri_id, data_obj, fotos)

            created.append({
                "id": str(asset.id),
                "santri_id": str(asset.santri_id),
                "jenis_aset": asset.jenis_aset,
                "jumlah": asset.jumlah,
                "nilai_perkiraan": asset.nilai_perkiraan,
                "foto_asset": [
                    {
                        "id": str(f.id),
                        "asset_id": str(f.asset_id),
                        "nama_file": f.nama_file,
                        "url_photo": f.url_photo
                    } for f in asset.foto_asset
                ]
            })

        meta = {"created_count": len(created)}
        return success_response(created, status_code=201, meta=meta)

    except Exception as e:
        return error_response(f"Failed to bulk create assets: {str(e)}", error_code="UPLOAD_ERROR")


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
