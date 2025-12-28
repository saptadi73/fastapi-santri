"""Routes for pesantren scoring calculation and retrieval."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pesantren_score_service import PesantrenScoreService
from app.schemas.pesantren_skor_schema import PesantrenSkorResponse
from app.supports import success_response, error_response
from app.models.pondok_pesantren import PondokPesantren

router = APIRouter(prefix="/api/pesantren-scoring", tags=["Pesantren Scoring"])


def get_service(db: Session = Depends(get_db)) -> PesantrenScoreService:
    """Dependency to get pesantren score service."""
    return PesantrenScoreService(db)


@router.post("/{pesantren_id}/calculate", response_model=None)
async def calculate_skor(
    pesantren_id: UUID,
    service: PesantrenScoreService = Depends(get_service)
):
    """Calculate and save scoring for a pesantren."""
    try:
        record = service.calculate_and_save(pesantren_id)
        return success_response(
            data=PesantrenSkorResponse.model_validate(record),
            message="Skor pesantren berhasil dihitung dan disimpan",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), error_code="INTERNAL_ERROR")


@router.get("/pesantren/{pesantren_id}", response_model=None)
async def get_skor_by_pesantren(
    pesantren_id: UUID,
    service: PesantrenScoreService = Depends(get_service)
):
    """Get scoring by pesantren ID."""
    record = service.get_by_pesantren_id(pesantren_id)
    if not record:
        return error_response(
            "Skor tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    return success_response(PesantrenSkorResponse.model_validate(record))


@router.get("/{skor_id}", response_model=None)
async def get_skor_detail(
    skor_id: UUID,
    service: PesantrenScoreService = Depends(get_service)
):
    """Get scoring detail by skor ID."""
    record = service.get_by_id(skor_id)
    if not record:
        return error_response(
            "Skor tidak ditemukan",
            status_code=404,
            error_code="NOT_FOUND"
        )
    return success_response(PesantrenSkorResponse.model_validate(record))


@router.post("/batch/calculate-all", response_model=None)
async def batch_calculate_all(db: Session = Depends(get_db)):
    """Calculate scoring for all pondok pesantren records."""
    try:
        service = PesantrenScoreService(db)
        pesantrens = db.query(PondokPesantren).all()
        
        results = []
        errors = []
        
        for pesantren in pesantrens:
            try:
                pesantren_id = (
                    UUID(str(pesantren.id))
                    if not isinstance(pesantren.id, UUID)
                    else pesantren.id
                )
                record = service.calculate_and_save(pesantren_id)
                results.append({
                    "pesantren_id": str(pesantren.id),
                    "nama": pesantren.nama,
                    "skor_total": record.skor_total,
                    "kategori": record.kategori_kelayakan,
                })
            except Exception as e:
                errors.append({
                    "pesantren_id": str(pesantren.id),
                    "nama": pesantren.nama,
                    "error": str(e),
                })
        
        return success_response(
            data={
                "total_processed": len(results),
                "total_errors": len(errors),
                "results": results,
                "errors": errors if errors else None,
            },
            message=f"Scoring selesai: {len(results)} berhasil, {len(errors)} gagal",
            status_code=200
        )
    except Exception as e:
        return error_response(str(e), error_code="INTERNAL_ERROR")
