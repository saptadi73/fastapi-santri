"""Routes for santri orangtua endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_orangtua_schema import (
    SantriOrangtuaCreate,
    SantriOrangtuaUpdate,
    SantriOrangtuaResponse,
    FotoOrangtuaResponse
)
from app.services.santri_orangtua_service import SantriOrangtuaService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/api/santri-orangtua", tags=["Santri Orangtua"])


def get_service(db: Session = Depends(get_db)) -> SantriOrangtuaService:
    """Dependency to get santri orangtua service."""
    return SantriOrangtuaService(db)


@router.get("", response_model=None)
async def get_all_orangtua(
    santri_id: Optional[UUID] = Query(None, description="Santri ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by nama or NIK"),
    hubungan: Optional[str] = Query(None, description="Filter by hubungan (ayah/ibu/wali)"),
    pesantren_id: Optional[UUID] = Query(None, description="Filter by pondok pesantren ID"),
    service: SantriOrangtuaService = Depends(get_service)
):
    """Get all orangtua for a santri with pagination and filters."""
    try:
        orangtua_list, total = service.get_all(
            santri_id=santri_id,
            page=page,
            per_page=per_page,
            search=search,
            hubungan=hubungan,
            pesantren_id=pesantren_id
        )
        
        result = []
        for orangtua in orangtua_list:
            fotos = [
                {
                    "id": str(foto.id),
                    "nama_file": foto.nama_file,
                    "url_photo": foto.url_photo
                }
                for foto in (orangtua.foto_orangtua or [])
            ]

            orangtua_dict = {
                "id": str(orangtua.id),
                "nama": orangtua.nama,
                "hubungan": orangtua.hubungan,
                "pekerjaan": orangtua.pekerjaan,
                "status_hidup": orangtua.status_hidup,
                "foto_count": len(fotos),
                "foto_orangtua": fotos
            }
            result.append(orangtua_dict)
        
        return paginated_response(
            data=result,
            page=page,
            per_page=per_page,
            total=total
        )
    except Exception as e:
        return error_response(f"Failed to fetch orangtua: {str(e)}", error_code="INTERNAL_ERROR")


@router.get("/{orangtua_id}", response_model=None)
async def get_orangtua_detail(
    orangtua_id: UUID,
    service: SantriOrangtuaService = Depends(get_service)
):
    """Get orangtua detail with photos."""
    try:
        orangtua = service.get_by_id(orangtua_id)
        
        if not orangtua:
            return error_response("Orangtua not found", error_code="NOT_FOUND")
        
        fotos = [
            {
                "id": str(foto.id),
                "orangtua_id": str(foto.orangtua_id),
                "nama_file": foto.nama_file,
                "url_photo": foto.url_photo
            }
            for foto in orangtua.foto_orangtua
        ]
        
        data = {
            "id": str(orangtua.id),
            "santri_id": str(orangtua.santri_id),
            "nama": orangtua.nama,
            "nik": orangtua.nik,
            "hubungan": orangtua.hubungan,
            "pendidikan": orangtua.pendidikan,
            "pekerjaan": orangtua.pekerjaan,
            "pendapatan_bulanan": orangtua.pendapatan_bulanan,
            "status_hidup": orangtua.status_hidup,
            "kontak_telepon": orangtua.kontak_telepon,
            "foto_orangtua": fotos
        }
        
        return success_response(data)
    except Exception as e:
        return error_response(f"Failed to fetch orangtua: {str(e)}", error_code="INTERNAL_ERROR")


@router.post("", response_model=None)
async def create_orangtua(
    request: Request,
    santri_id: UUID = Form(...),
    nama: str = Form(...),
    hubungan: str = Form(...),
    nik: Optional[str] = Form(None),
    pendidikan: Optional[str] = Form(None),
    pekerjaan: Optional[str] = Form(None),
    pendapatan_bulanan: Optional[int] = Form(None),
    status_hidup: Optional[str] = Form(None),
    kontak_telepon: Optional[str] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriOrangtuaService = Depends(get_service)
):
    """Create new orangtua with optional photos."""
    try:
        # Validate hubungan
        if hubungan not in ["ayah", "ibu", "wali"]:
            return error_response(
                "hubungan must be 'ayah', 'ibu', or 'wali'",
                error_code="VALIDATION_ERROR"
            )
        
        # Validate status_hidup if provided
        if status_hidup and status_hidup not in ["hidup", "meninggal"]:
            return error_response(
                "status_hidup must be 'hidup' or 'meninggal'",
                error_code="VALIDATION_ERROR"
            )
        
        data = SantriOrangtuaCreate(
            santri_id=santri_id,
            nama=nama,
            nik=nik,
            hubungan=hubungan,
            pendidikan=pendidikan,
            pekerjaan=pekerjaan,
            pendapatan_bulanan=pendapatan_bulanan,
            status_hidup=status_hidup,
            kontak_telepon=kontak_telepon
        )
        
        # Support multiple possible file field names: fotos / foto_files / files / foto_orangtua
        if not fotos or (isinstance(fotos, list) and len(fotos) == 0):
            form = await request.form()
            collected: List[UploadFile] = []
            for key, val in form.multi_items():
                if isinstance(val, UploadFile) and key in {"fotos", "foto_files", "files", "foto_orangtua"}:
                    collected.append(val)
            fotos = collected if collected else None

        orangtua = await service.create(santri_id, data, fotos)
        
        fotos_response = [
            {
                "id": str(f.id),
                "orangtua_id": str(f.orangtua_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in orangtua.foto_orangtua
        ]
        
        result = {
            "id": str(orangtua.id),
            "santri_id": str(orangtua.santri_id),
            "nama": orangtua.nama,
            "nik": orangtua.nik,
            "hubungan": orangtua.hubungan,
            "pendidikan": orangtua.pendidikan,
            "pekerjaan": orangtua.pekerjaan,
            "pendapatan_bulanan": orangtua.pendapatan_bulanan,
            "status_hidup": orangtua.status_hidup,
            "kontak_telepon": orangtua.kontak_telepon,
            "foto_orangtua": fotos_response
        }
        
        return success_response(result, status_code=201)
        
    except ValueError as e:
        return error_response(str(e), error_code="VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Failed to create orangtua: {str(e)}", error_code="UPLOAD_ERROR")


@router.post("/{orangtua_id}/photos", response_model=None)
async def add_orangtua_photos(
    orangtua_id: UUID,
    fotos: List[UploadFile] = File(...),
    service: SantriOrangtuaService = Depends(get_service)
):
    """Add photos to existing orangtua."""
    try:
        if not fotos:
            return error_response("No files provided", error_code="VALIDATION_ERROR")
        
        fotos_obj = await service.add_photos(orangtua_id, fotos)
        
        result = [
            {
                "id": str(f.id),
                "orangtua_id": str(f.orangtua_id),
                "nama_file": f.nama_file,
                "url_photo": f.url_photo
            }
            for f in fotos_obj
        ]
        
        return success_response(result, status_code=201)
        
    except Exception as e:
        return error_response(f"Failed to upload photos: {str(e)}", error_code="UPLOAD_ERROR")


@router.put("/photos/{foto_id}", response_model=None)
async def update_orangtua_photo(
    foto_id: UUID,
    foto: UploadFile = File(...),
    service: SantriOrangtuaService = Depends(get_service)
):
    """Replace an orangtua photo with a new one."""
    try:
        updated_foto = await service.update_photo(foto_id, foto)
        
        if not updated_foto:
            return error_response("Photo not found", error_code="NOT_FOUND")
        
        result = {
            "id": str(updated_foto.id),
            "orangtua_id": str(updated_foto.orangtua_id),
            "nama_file": updated_foto.nama_file,
            "url_photo": updated_foto.url_photo
        }
        
        return success_response(result, message="Photo updated successfully")
        
    except Exception as e:
        return error_response(f"Failed to update photo: {str(e)}", error_code="UPLOAD_ERROR")


@router.put("/{orangtua_id}", response_model=None)
async def update_orangtua(
    request: Request,
    orangtua_id: UUID,
    nama: Optional[str] = Form(None),
    nik: Optional[str] = Form(None),
    hubungan: Optional[str] = Form(None),
    pendidikan: Optional[str] = Form(None),
    pekerjaan: Optional[str] = Form(None),
    pendapatan_bulanan: Optional[int] = Form(None),
    status_hidup: Optional[str] = Form(None),
    kontak_telepon: Optional[str] = Form(None),
    fotos: Optional[List[UploadFile]] = File(None),
    service: SantriOrangtuaService = Depends(get_service)
):
    """Update orangtua by ID with optional new photos (multipart/form-data)."""
    try:
        # Validate hubungan if provided
        if hubungan and hubungan not in ["ayah", "ibu", "wali"]:
            return error_response(
                "hubungan must be 'ayah', 'ibu', or 'wali'",
                error_code="VALIDATION_ERROR"
            )
        
        # Validate status_hidup if provided
        if status_hidup and status_hidup not in ["hidup", "meninggal"]:
            return error_response(
                "status_hidup must be 'hidup' or 'meninggal'",
                error_code="VALIDATION_ERROR"
            )
        
        data = SantriOrangtuaUpdate(
            nama=nama,
            nik=nik,
            hubungan=hubungan,
            pendidikan=pendidikan,
            pekerjaan=pekerjaan,
            pendapatan_bulanan=pendapatan_bulanan,
            status_hidup=status_hidup,
            kontak_telepon=kontak_telepon
        )

        # Fallback collect files if bound param is empty/missing
        if not fotos or (isinstance(fotos, list) and len(fotos) == 0):
            form = await request.form()
            collected: List[UploadFile] = []
            for key, val in form.multi_items():
                if isinstance(val, UploadFile) and key in {"fotos", "foto_files", "files", "foto_orangtua"}:
                    collected.append(val)
            fotos = collected if collected else None
        
        orangtua = await service.update(orangtua_id, data, fotos)
        
        if not orangtua:
            return error_response(
                message="Orangtua not found",
                error_code="NOT_FOUND"
            )
        
        fotos_resp = [
            {
                "id": str(foto.id),
                "orangtua_id": str(foto.orangtua_id),
                "nama_file": foto.nama_file,
                "url_photo": foto.url_photo
            }
            for foto in orangtua.foto_orangtua
        ]
        
        result = {
            "id": str(orangtua.id),
            "santri_id": str(orangtua.santri_id),
            "nama": orangtua.nama,
            "nik": orangtua.nik,
            "hubungan": orangtua.hubungan,
            "pendidikan": orangtua.pendidikan,
            "pekerjaan": orangtua.pekerjaan,
            "pendapatan_bulanan": orangtua.pendapatan_bulanan,
            "status_hidup": orangtua.status_hidup,
            "kontak_telepon": orangtua.kontak_telepon,
            "foto_orangtua": fotos_resp
        }
        
        return success_response(result)
    except ValueError as e:
        return error_response(str(e), error_code="VALIDATION_ERROR")
    except Exception as e:
        return error_response(f"Failed to update orangtua: {str(e)}", error_code="INTERNAL_ERROR")


@router.delete("/{orangtua_id}", response_model=None)
async def delete_orangtua(
    orangtua_id: UUID,
    service: SantriOrangtuaService = Depends(get_service)
):
    """Delete orangtua and related photos."""
    try:
        success = await service.delete(orangtua_id)
        
        if not success:
            return error_response("Orangtua not found", error_code="NOT_FOUND")
        
        return success_response({"message": "Orangtua deleted successfully"})
        
    except Exception as e:
        return error_response(f"Failed to delete orangtua: {str(e)}", error_code="INTERNAL_ERROR")
