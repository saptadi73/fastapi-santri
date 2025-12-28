"""Alias router for santri pribadi endpoints under /santri-pribadi."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.santri_pribadi_schema import (
    SantriPribadiCreate,
    SantriPribadiUpdate,
    SantriPribadiResponse,
    FotoSantriResponse,
)
from app.services.santri_pribadi_service import SantriPribadiService
from app.supports import success_response, error_response, paginated_response

router = APIRouter(prefix="/santri-pribadi", tags=["Santri Pribadi (Alias)"])


def get_service(db: Session = Depends(get_db)) -> SantriPribadiService:
    return SantriPribadiService(db)


@router.get("", response_model=None)
async def get_all_santri(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    provinsi: Optional[str] = Query(None),
    kabupaten: Optional[str] = Query(None),
    jenis_kelamin: Optional[str] = Query(None),
    pesantren_id: Optional[UUID] = Query(None),
    service: SantriPribadiService = Depends(get_service),
):
    santri_list, total = service.get_all(
        page=page,
        per_page=per_page,
        search=search,
        provinsi=provinsi,
        kabupaten=kabupaten,
        jenis_kelamin=jenis_kelamin,
        pesantren_id=pesantren_id,
    )

    result = []
    for santri in santri_list:
        result.append({
            "id": santri.id,
            "nama": santri.nama,
            "nik": santri.nik,
            "jenis_kelamin": santri.jenis_kelamin,
            "provinsi": santri.provinsi,
            "kabupaten": santri.kabupaten,
            "foto_count": len(santri.foto_santri),
            "pesantren_id": getattr(santri, "pesantren_id", None),
            "pesantren_nama": santri.pesantren.nama if getattr(santri, "pesantren", None) else None,
        })

    return paginated_response(
        data=result,
        page=page,
        per_page=per_page,
        total=total,
        message="Data santri berhasil diambil",
    )


@router.get("/{santri_id}", response_model=None)
async def get_santri_detail(
    santri_id: UUID,
    service: SantriPribadiService = Depends(get_service),
):
    santri = service.get_by_id(santri_id)
    if not santri:
        return error_response(message="Santri tidak ditemukan", status_code=404)
    return success_response(
        data=SantriPribadiResponse.model_validate(santri),
        message="Detail santri berhasil diambil",
    )


@router.post("", response_model=None)
async def create_santri(
    pesantren_id: UUID = Form(...),
    nama: str = Form(...),
    jenis_kelamin: str = Form(...),
    nik: Optional[str] = Form(None),
    no_kk: Optional[str] = Form(None),
    tempat_lahir: Optional[str] = Form(None),
    tanggal_lahir: Optional[str] = Form(None),
    status_tinggal: Optional[str] = Form(None),
    lama_mondok_tahun: Optional[int] = Form(None),
    provinsi: Optional[str] = Form(None),
    kabupaten: Optional[str] = Form(None),
    kecamatan: Optional[str] = Form(None),
    desa: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    foto_files: List[UploadFile] = File(None),
    service: SantriPribadiService = Depends(get_service),
):
    try:
        from datetime import datetime
        parsed_tanggal = None
        if tanggal_lahir:
            try:
                parsed_tanggal = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
            except ValueError:
                return error_response(
                    message="Format tanggal_lahir tidak valid, gunakan YYYY-MM-DD",
                    status_code=400,
                )

        santri_data = SantriPribadiCreate(
            pesantren_id=pesantren_id,
            nama=nama,
            jenis_kelamin=jenis_kelamin,
            nik=nik,
            no_kk=no_kk,
            tempat_lahir=tempat_lahir,
            tanggal_lahir=parsed_tanggal,
            status_tinggal=status_tinggal,
            lama_mondok_tahun=lama_mondok_tahun,
            provinsi=provinsi,
            kabupaten=kabupaten,
            kecamatan=kecamatan,
            desa=desa,
            latitude=latitude,
            longitude=longitude,
        )

        santri = await service.create(santri_data, foto_files)
        return success_response(
            data=SantriPribadiResponse.model_validate(santri),
            message="Santri berhasil ditambahkan",
            status_code=201,
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@router.put("/{santri_id}", response_model=None)
async def update_santri(
    santri_id: UUID,
    pesantren_id: Optional[UUID] = Form(None),
    nama: Optional[str] = Form(None),
    jenis_kelamin: Optional[str] = Form(None),
    nik: Optional[str] = Form(None),
    no_kk: Optional[str] = Form(None),
    tempat_lahir: Optional[str] = Form(None),
    tanggal_lahir: Optional[str] = Form(None),
    status_tinggal: Optional[str] = Form(None),
    lama_mondok_tahun: Optional[int] = Form(None),
    provinsi: Optional[str] = Form(None),
    kabupaten: Optional[str] = Form(None),
    kecamatan: Optional[str] = Form(None),
    desa: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    service: SantriPribadiService = Depends(get_service),
):
    try:
        from datetime import datetime
        parsed_tanggal = None
        if tanggal_lahir:
            try:
                parsed_tanggal = datetime.strptime(tanggal_lahir, "%Y-%m-%d").date()
            except ValueError:
                return error_response(
                    message="Format tanggal_lahir tidak valid, gunakan YYYY-MM-DD",
                    status_code=400,
                )

        update_data = SantriPribadiUpdate(
            pesantren_id=pesantren_id,
            nama=nama,
            jenis_kelamin=jenis_kelamin,
            nik=nik,
            no_kk=no_kk,
            tempat_lahir=tempat_lahir,
            tanggal_lahir=parsed_tanggal,
            status_tinggal=status_tinggal,
            lama_mondok_tahun=lama_mondok_tahun,
            provinsi=provinsi,
            kabupaten=kabupaten,
            kecamatan=kecamatan,
            desa=desa,
            latitude=latitude,
            longitude=longitude,
        )

        santri = service.update(santri_id, update_data)
        if not santri:
            return error_response(message="Santri tidak ditemukan", status_code=404)
        return success_response(
            data=SantriPribadiResponse.model_validate(santri),
            message="Santri berhasil diupdate",
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@router.delete("/{santri_id}", response_model=None)
async def delete_santri(
    santri_id: UUID,
    service: SantriPribadiService = Depends(get_service),
):
    success = service.delete(santri_id)
    if not success:
        return error_response(message="Santri tidak ditemukan", status_code=404)
    return success_response(message="Santri dan foto berhasil dihapus")


@router.post("/{santri_id}/photos", response_model=None)
async def add_santri_photos(
    santri_id: UUID,
    foto_files: List[UploadFile] = File(...),
    service: SantriPribadiService = Depends(get_service),
):
    try:
        foto_list = await service.add_photos(santri_id, foto_files)
        return success_response(
            data=[FotoSantriResponse.model_validate(foto) for foto in foto_list],
            message=f"{len(foto_list)} foto berhasil ditambahkan",
            status_code=201,
        )
    except HTTPException as e:
        return error_response(message=e.detail, status_code=e.status_code)
    except Exception as e:
        return error_response(message=f"Terjadi kesalahan: {str(e)}", status_code=500)


@router.delete("/photos/{foto_id}", response_model=None)
async def delete_santri_photo(
    foto_id: UUID,
    service: SantriPribadiService = Depends(get_service),
):
    success = service.delete_photo(foto_id)
    if not success:
        return error_response(message="Foto tidak ditemukan", status_code=404)
    return success_response(message="Foto berhasil dihapus")
