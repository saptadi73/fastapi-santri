"""Routes for scoring calculation and retrieval."""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.score_service import ScoreService
from app.schemas.santri_skor_schema import SantriSkorResponse
from app.supports import success_response, error_response
from app.models.santri_pribadi import SantriPribadi

router = APIRouter(prefix="/api/scoring", tags=["Scoring"])


class BulkScoreRequest(BaseModel):
    """Request body for bulk asset scoring."""
    santri_ids: List[UUID] = []
    metode: str = "rules.v1"
    version: str = "1.0.0"


def get_service(db: Session = Depends(get_db)) -> ScoreService:
    return ScoreService(db)


@router.post("/{santri_id}/calculate", response_model=None)
async def calculate_skor(santri_id: UUID, service: ScoreService = Depends(get_service)):
    try:
        record, breakdown = service.calculate_and_save(santri_id)
        # Convert to response schema with breakdown
        response_data = SantriSkorResponse.model_validate(record)
        response_dict = response_data.model_dump()
        response_dict["breakdown"] = breakdown
        return success_response(
            data=response_dict,
            message="Skor berhasil dihitung dan disimpan",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), error_code="INTERNAL_ERROR")


@router.get("/santri/{santri_id}", response_model=None)
async def get_skor_by_santri(santri_id: UUID, service: ScoreService = Depends(get_service)):
    result = service.get_by_santri_id(santri_id)
    if not result:
        return error_response("Skor tidak ditemukan", status_code=404, error_code="NOT_FOUND")
    
    record, breakdown = result
    # Convert to response schema with breakdown
    response_data = SantriSkorResponse.model_validate(record)
    response_dict = response_data.model_dump()
    response_dict["breakdown"] = breakdown
    return success_response(response_dict)


@router.post("/bulk/calculate-asset", response_model=None)
async def bulk_calculate_asset_scores(
    payload: BulkScoreRequest,
    service: ScoreService = Depends(get_service)
):
    """Bulk calculate asset scores for multiple santri.
    
    This endpoint calculates complete scores (including asset component) for multiple santri at once.
    Useful when assets have been added/updated and you need to recalculate scoring.
    """
    try:
        if not payload.santri_ids:
            return error_response("santri_ids tidak boleh kosong", error_code="VALIDATION_ERROR")

        results = []
        errors = []

        for santri_id in payload.santri_ids:
            try:
                record, _ = service.calculate_and_save(santri_id, metode=payload.metode, version=payload.version)
                results.append({
                    "santri_id": str(santri_id),
                    "skor_total": record.skor_total,
                    "skor_aset": record.skor_aset,
                    "kategori_kemiskinan": record.kategori_kemiskinan,
                    "success": True
                })
            except Exception as e:
                errors.append({
                    "santri_id": str(santri_id),
                    "error": str(e),
                    "success": False
                })

        return success_response(
            data={
                "total_requested": len(payload.santri_ids),
                "total_success": len(results),
                "total_errors": len(errors),
                "results": results,
                "errors": errors if errors else []
            },
            message=f"Bulk scoring selesai: {len(results)} berhasil, {len(errors)} gagal",
            status_code=201
        )
    except Exception as e:
        return error_response(f"Failed to bulk calculate scores: {str(e)}", error_code="INTERNAL_ERROR")


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
                record, _ = service.calculate_and_save(santri_id)
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

