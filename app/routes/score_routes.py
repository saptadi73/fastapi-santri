"""Routes for scoring calculation and retrieval."""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.score_service import ScoreService
from app.schemas.santri_skor_schema import SantriSkorResponse
from app.supports import success_response, error_response
from app.models.santri_pribadi import SantriPribadi

router = APIRouter(prefix="/api/scoring", tags=["Scoring"])


def get_service(db: Session = Depends(get_db)) -> ScoreService:
    return ScoreService(db)


@router.post("/{santri_id}/calculate", response_model=None)
async def calculate_skor(santri_id: UUID, service: ScoreService = Depends(get_service)):
    try:
        record = service.calculate_and_save(santri_id)
        return success_response(
            data=SantriSkorResponse.model_validate(record),
            message="Skor berhasil dihitung dan disimpan",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), error_code="INTERNAL_ERROR")


@router.get("/santri/{santri_id}", response_model=None)
async def get_skor_by_santri(santri_id: UUID, service: ScoreService = Depends(get_service)):
    record = service.get_by_santri_id(santri_id)
    if not record:
        return error_response("Skor tidak ditemukan", status_code=404, error_code="NOT_FOUND")
    return success_response(SantriSkorResponse.model_validate(record))


@router.get("/{skor_id}", response_model=None)
async def get_skor_detail(skor_id: UUID, service: ScoreService = Depends(get_service)):
    record = service.get_by_id(skor_id)
    if not record:
        return error_response("Skor tidak ditemukan", status_code=404, error_code="NOT_FOUND")
    return success_response(SantriSkorResponse.model_validate(record))


@router.post("/batch/calculate-all", response_model=None)
async def batch_calculate_all(db: Session = Depends(get_db)):
    """Calculate scoring for all santri_pribadi records."""
    try:
        service = ScoreService(db)
        santris = db.query(SantriPribadi).all()
        
        results = []
        errors = []
        
        for santri in santris:
            try:
                santri_id = UUID(str(santri.id)) if not isinstance(santri.id, UUID) else santri.id
                record = service.calculate_and_save(santri_id)
                results.append({
                    "santri_id": str(santri.id),
                    "nama": santri.nama,
                    "skor_total": record.skor_total,
                    "kategori": record.kategori_kemiskinan,
                })
            except Exception as e:
                errors.append({
                    "santri_id": str(santri.id),
                    "nama": santri.nama,
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

