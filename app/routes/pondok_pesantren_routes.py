"""API routes for pondok pesantren CRUD operations."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.file_utils import FileUploader
from app.services.pondok_pesantren_service import PondokPesantrenService
from app.schemas.pondok_pesantren_schema import (
    PondokPesantrenResponse,
    PondokPesantrenCreate,
    PondokPesantrenUpdate,
    PaginatedPesantrenResponse,
    PondokPesantrenListResponse,
    PondokPesantrenDropdownResponse
)

router = APIRouter(prefix="/pondok-pesantren", tags=["Pondok Pesantren"])


@router.get("/dropdown", response_model=List[PondokPesantrenDropdownResponse])
def list_pesantren_dropdown(
    search: Optional[str] = Query(None, description="Optional search by nama, nsp, kabupaten, provinsi"),
    db: Session = Depends(get_db)
):
    """Get all pondok pesantren for dropdown list (optional search, no pagination)."""
    service = PondokPesantrenService(db)
    results = service.get_all_for_dropdown(search=search)
    return [PondokPesantrenDropdownResponse.model_validate(p) for p in results]


@router.get("", response_model=PaginatedPesantrenResponse)
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
    
    # Convert to response schema
    data = [PondokPesantrenListResponse.model_validate(p) for p in results]
    
    return {
        "data": data,
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
async def create_pesantren(
    nama: str = Form(...),
    nsp: Optional[str] = Form(None),
    tahun_berdiri: Optional[int] = Form(None),
    jumlah_santri: Optional[int] = Form(None),
    jumlah_guru: Optional[int] = Form(None),
    alamat: Optional[str] = Form(None),
    desa: Optional[str] = Form(None),
    kecamatan: Optional[str] = Form(None),
    kabupaten: Optional[str] = Form(None),
    provinsi: Optional[str] = Form(None),
    kode_pos: Optional[str] = Form(None),
    telepon: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    nama_kyai: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    foto: Optional[UploadFile] = File(None),
    foto_files: Optional[list[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Create new pondok pesantren with optional photo upload."""
    
    # Collect all photos
    saved_photo_paths: list[str] = []

    # Validate and save single main photo if provided
    if foto:
        is_valid, error = FileUploader.validate_image(foto)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        try:
            saved_photo_paths.append(
                await FileUploader.save_upload_file(
                    foto,
                    subfolder="pesantren",
                    prefix="pesantren_"
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

    # Validate and save multiple photos if provided
    if foto_files:
        for f in foto_files:
            if not f or not f.filename:
                continue
            is_valid, error = FileUploader.validate_image(f)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            try:
                saved_photo_paths.append(
                    await FileUploader.save_upload_file(
                        f,
                        subfolder="pesantren",
                        prefix="pesantren_"
                    )
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    
    # Create data object
    data = PondokPesantrenCreate(
        nama=nama,
        nsp=nsp,
        tahun_berdiri=tahun_berdiri,
        jumlah_santri=jumlah_santri,
        jumlah_guru=jumlah_guru,
        alamat=alamat,
        desa=desa,
        kecamatan=kecamatan,
        kabupaten=kabupaten,
        provinsi=provinsi,
        kode_pos=kode_pos,
        telepon=telepon,
        email=email,
        website=website,
        nama_kyai=nama_kyai,
        latitude=latitude,
        longitude=longitude,
        foto_path=saved_photo_paths[0] if saved_photo_paths else None
    )
    
    service = PondokPesantrenService(db)
    pesantren = service.create(data)

    # Persist all photos to foto_pesantren table
    if saved_photo_paths:
        service.add_photos(pesantren.id, saved_photo_paths)
        pesantren = service.get_by_id(pesantren.id)

    return pesantren


@router.put("/{pesantren_id}", response_model=PondokPesantrenResponse)
async def update_pesantren(
    pesantren_id: UUID,
    nama: Optional[str] = Form(None),
    nsp: Optional[str] = Form(None),
    tahun_berdiri: Optional[int] = Form(None),
    jumlah_santri: Optional[int] = Form(None),
    jumlah_guru: Optional[int] = Form(None),
    alamat: Optional[str] = Form(None),
    desa: Optional[str] = Form(None),
    kecamatan: Optional[str] = Form(None),
    kabupaten: Optional[str] = Form(None),
    provinsi: Optional[str] = Form(None),
    kode_pos: Optional[str] = Form(None),
    telepon: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    nama_kyai: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    foto: Optional[UploadFile] = File(None),
    foto_files: Optional[list[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """Update pondok pesantren data with optional photo upload."""
    service = PondokPesantrenService(db)

    existing = service.get_by_id(pesantren_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Pesantren tidak ditemukan")

    # Validate and save new main photo if provided
    foto_path = None
    if foto:
        is_valid, error = FileUploader.validate_image(foto)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        try:
            foto_path = await FileUploader.save_upload_file(
                foto,
                subfolder="pesantren",
                prefix="pesantren_"
            )
            # Delete old photo if exists
            if existing.foto_path:
                FileUploader.delete_file(existing.foto_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

    # Save extra photos
    extra_paths: list[str] = []
    if foto_files:
        for f in foto_files:
            if not f or not f.filename:
                continue
            is_valid, error = FileUploader.validate_image(f)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            try:
                extra_paths.append(
                    await FileUploader.save_upload_file(
                        f,
                        subfolder="pesantren",
                        prefix="pesantren_"
                    )
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

    # Create update data object
    data = PondokPesantrenUpdate(
        nama=nama,
        nsp=nsp,
        tahun_berdiri=tahun_berdiri,
        jumlah_santri=jumlah_santri,
        jumlah_guru=jumlah_guru,
        alamat=alamat,
        desa=desa,
        kecamatan=kecamatan,
        kabupaten=kabupaten,
        provinsi=provinsi,
        kode_pos=kode_pos,
        telepon=telepon,
        email=email,
        website=website,
        nama_kyai=nama_kyai,
        latitude=latitude,
        longitude=longitude,
        foto_path=foto_path
    )

    pesantren = service.update(pesantren_id, data)
    if pesantren and extra_paths:
        service.add_photos(pesantren_id, extra_paths)
        pesantren = service.get_by_id(pesantren_id)

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
