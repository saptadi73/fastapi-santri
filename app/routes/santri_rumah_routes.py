"""Routes for santri rumah endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Form, UploadFile, File, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_rumah_schema import (
    SantriRumahCreate,
    SantriRumahUpdate,
    SantriRumahResponse,
    FotoRumahResponse
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
    """Get rumah detail by ID with photos."""
    rumah = service.get_by_id(rumah_id)
    if not rumah:
        return error_response(
            message="Data rumah tidak ditemukan",
            status_code=404
        )
    
    result = {
        "id": str(rumah.id),
        "santri_id": str(rumah.santri_id),
        "status_rumah": rumah.status_rumah,
        "jenis_lantai": rumah.jenis_lantai,
        "jenis_dinding": rumah.jenis_dinding,
        "jenis_atap": rumah.jenis_atap,
        "akses_air_bersih": rumah.akses_air_bersih,
        "daya_listrik_va": rumah.daya_listrik_va,
        "foto_rumah": [
            {
                "id": str(f.id),
                "rumah_id": str(f.rumah_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in rumah.foto_rumah
        ]
    }
    
    return success_response(
        data=result,
        message="Detail rumah berhasil diambil"
    )


@router.get("/santri/{santri_id}", response_model=None)
async def get_rumah_by_santri(
    santri_id: UUID,
    service: SantriRumahService = Depends(get_service)
):
    """Get rumah by santri ID with photos."""
    rumah = service.get_by_santri_id(santri_id)
    if not rumah:
        return error_response(
            message="Data rumah untuk santri ini tidak ditemukan",
            status_code=404
        )
    
    result = {
        "id": str(rumah.id),
        "santri_id": str(rumah.santri_id),
        "status_rumah": rumah.status_rumah,
        "jenis_lantai": rumah.jenis_lantai,
        "jenis_dinding": rumah.jenis_dinding,
        "jenis_atap": rumah.jenis_atap,
        "akses_air_bersih": rumah.akses_air_bersih,
        "daya_listrik_va": rumah.daya_listrik_va,
        "foto_rumah": [
            {
                "id": str(f.id),
                "rumah_id": str(f.rumah_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in rumah.foto_rumah
        ]
    }
    
    return success_response(
        data=result,
        message="Data rumah berhasil diambil"
    )


@router.post("", response_model=None)
async def create_rumah(
    santri_id: UUID = Form(...),
    status_rumah: str = Form(...),
    jenis_lantai: str = Form(...),
    jenis_dinding: str = Form(...),
    jenis_atap: str = Form(...),
    akses_air_bersih: str = Form(...),
    daya_listrik_va: Optional[str] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriRumahService = Depends(get_service)
):
    """Create new rumah record with optional photos (multipart/form-data)."""
    try:
        data = SantriRumahCreate(
            santri_id=santri_id,
            status_rumah=status_rumah,
            jenis_lantai=jenis_lantai,
            jenis_dinding=jenis_dinding,
            jenis_atap=jenis_atap,
            akses_air_bersih=akses_air_bersih,
            daya_listrik_va=daya_listrik_va
        )
        
        rumah = await service.create(data, fotos)
        
        result = {
            "id": str(rumah.id),
            "santri_id": str(rumah.santri_id),
            "status_rumah": rumah.status_rumah,
            "jenis_lantai": rumah.jenis_lantai,
            "jenis_dinding": rumah.jenis_dinding,
            "jenis_atap": rumah.jenis_atap,
            "akses_air_bersih": rumah.akses_air_bersih,
            "daya_listrik_va": rumah.daya_listrik_va,
            "foto_rumah": [
                {
                    "id": str(f.id),
                    "rumah_id": str(f.rumah_id),
                    "nama_file": f.nama_file,
                    "url_photo": f.url_photo
                }
                for f in rumah.foto_rumah
            ]
        }
        
        return success_response(
            data=result,
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
    status_rumah: Optional[str] = Form(None),
    jenis_lantai: Optional[str] = Form(None),
    jenis_dinding: Optional[str] = Form(None),
    jenis_atap: Optional[str] = Form(None),
    akses_air_bersih: Optional[str] = Form(None),
    daya_listrik_va: Optional[str] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriRumahService = Depends(get_service)
):
    """Update rumah data with optional photos (multipart/form-data)."""
    try:
        data = SantriRumahUpdate(
            status_rumah=status_rumah,
            jenis_lantai=jenis_lantai,
            jenis_dinding=jenis_dinding,
            jenis_atap=jenis_atap,
            akses_air_bersih=akses_air_bersih,
            daya_listrik_va=daya_listrik_va
        )
        
        rumah = await service.update(rumah_id, data, fotos)
        if not rumah:
            return error_response(
                message="Data rumah tidak ditemukan",
                status_code=404,
                error_code="NOT_FOUND"
            )
        
        result = {
            "id": str(rumah.id),
            "santri_id": str(rumah.santri_id),
            "status_rumah": rumah.status_rumah,
            "jenis_lantai": rumah.jenis_lantai,
            "jenis_dinding": rumah.jenis_dinding,
            "jenis_atap": rumah.jenis_atap,
            "akses_air_bersih": rumah.akses_air_bersih,
            "daya_listrik_va": rumah.daya_listrik_va,
            "foto_rumah": [
                {
                    "id": str(f.id),
                    "rumah_id": str(f.rumah_id),
                    "nama_file": f.nama_file,
                    "url_photo": f.url_photo
                }
                for f in rumah.foto_rumah
            ]
        }
        
        return success_response(
            data=result,
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
    """Delete rumah by ID and all related photos."""
    success = await service.delete(rumah_id)
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


@router.post("/{rumah_id}/photos", response_model=None)
async def add_rumah_photos(
    rumah_id: UUID,
    fotos: List[UploadFile] = File(...),
    service: SantriRumahService = Depends(get_service)
):
    """Add photos to existing rumah."""
    try:
        if not fotos:
            return error_response("No files provided", error_code="VALIDATION_ERROR")
        
        fotos_obj = await service.add_photos(rumah_id, fotos)
        
        result = [
            {
                "id": str(f.id),
                "rumah_id": str(f.rumah_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in fotos_obj
        ]
        
        return success_response(result, status_code=201)
        
    except Exception as e:
        return error_response(f"Failed to upload photos: {str(e)}", error_code="UPLOAD_ERROR")


@router.put("/photos/{foto_id}", response_model=None)
async def update_rumah_photo(
    foto_id: UUID,
    foto: UploadFile = File(...),
    service: SantriRumahService = Depends(get_service)
):
    """Replace a rumah photo with a new one."""
    try:
        updated_foto = await service.update_photo(foto_id, foto)
        
        if not updated_foto:
            return error_response("Photo not found", error_code="NOT_FOUND")
        
        result = {
            "id": str(updated_foto.id),
            "rumah_id": str(updated_foto.rumah_id),
            "nama_file": updated_foto.nama_file,
            "url_photo": updated_foto.url_photo
        }
        
        return success_response(result, message="Photo updated successfully")
        
    except Exception as e:
        return error_response(f"Failed to update photo: {str(e)}", error_code="UPLOAD_ERROR")


@router.delete("/photos/{foto_id}", response_model=None)
async def delete_rumah_photo(
    foto_id: UUID,
    service: SantriRumahService = Depends(get_service)
):
    """Delete single rumah photo."""
    try:
        success = await service.delete_photo(foto_id)
        
        if not success:
            return error_response("Photo not found", error_code="NOT_FOUND")
        
        return success_response({"message": "Photo deleted successfully"})
        
    except Exception as e:
        return error_response(f"Failed to delete photo: {str(e)}", error_code="INTERNAL_ERROR")
