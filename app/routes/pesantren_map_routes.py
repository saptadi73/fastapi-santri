"""Routes for Pesantren Map GIS API."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.pesantren_map_service import PesantrenMapService
from app.supports import success_response, error_response

router = APIRouter(prefix="/pesantren-map", tags=["Pesantren Map GIS"])


@router.get("/geojson", response_model=None)
def get_pesantren_geojson(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kelayakan"),
    provinsi: Optional[str] = Query(None, description="Filter by provinsi"),
    kabupaten: Optional[str] = Query(None, description="Filter by kabupaten"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """
    Get all pesantren as GeoJSON FeatureCollection for mapping.
    
    **Use Case:**
    - Display pesantren locations on map
    - Filter by quality category
    - Filter by region
    
    **Response Format:** GeoJSON FeatureCollection
    """
    try:
        service = PesantrenMapService(db)
        geojson = service.get_all_geojson(
            kategori=kategori,
            provinsi=provinsi,
            kabupaten=kabupaten,
            limit=limit
        )
        return geojson
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/bbox", response_model=None)
def get_pesantren_by_bbox(
    min_lon: float = Query(..., description="Minimum longitude"),
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lon: float = Query(..., description="Maximum longitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    kategori: Optional[str] = Query(None, description="Filter by kategori_kelayakan"),
    db: Session = Depends(get_db)
):
    """
    Get pesantren within bounding box.
    
    **Use Case:**
    - Get pesantren visible in map viewport
    - Optimize map loading
    
    **Example:**
    ```
    GET /api/pesantren-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2
    ```
    """
    try:
        service = PesantrenMapService(db)
        records = service.get_by_bounding_box(
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            kategori=kategori
        )
        
        data = []
        for r in records:
            # Extract lat/lon from geometry
            if r.lokasi is not None:
                result = db.execute(
                    text(f"SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM pesantren_map WHERE id = '{r.id}'")
                ).first()
                data.append({
                    "id": str(r.id),
                    "pesantren_id": str(r.pesantren_id),
                    "nama": r.nama,
                    "nsp": r.nsp,
                    "skor_terakhir": r.skor_terakhir,
                    "kategori_kelayakan": r.kategori_kelayakan,
                    "kabupaten": r.kabupaten,
                    "provinsi": r.provinsi,
                    "jumlah_santri": r.jumlah_santri,
                    "latitude": result.lat if result else None,
                    "longitude": result.lon if result else None
                })
        
        return success_response(data=data, message=f"Found {len(data)} pesantren")
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/statistics", response_model=None)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about pesantren map data.
    
    **Returns:**
    - Total pesantren
    - Pesantren with/without location
    - Count by quality category
    """
    try:
        service = PesantrenMapService(db)
        stats = service.get_statistics()
        return success_response(data=stats, message="Statistics retrieved successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=500)
