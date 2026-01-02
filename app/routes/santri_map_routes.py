"""Routes for Santri Map GIS API."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.santri_map_service import SantriMapService
from app.supports import success_response, error_response

router = APIRouter(prefix="/santri-map", tags=["Santri Map GIS"])


@router.get("/geojson", response_model=None)
def get_santri_geojson(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kemiskinan"),
    pesantren_id: Optional[UUID] = Query(None, description="Filter by pesantren"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """
    Get all santri as GeoJSON FeatureCollection for mapping.
    
    **Use Case:**
    - Display santri locations on map
    - Filter by poverty category
    - Filter by pesantren
    
    **Response Format:** GeoJSON FeatureCollection
    """
    try:
        service = SantriMapService(db)
        geojson = service.get_all_geojson(
            kategori=kategori,
            pesantren_id=pesantren_id,
            limit=limit
        )
        return geojson
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/bbox", response_model=None)
def get_santri_by_bbox(
    min_lon: float = Query(..., description="Minimum longitude"),
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lon: float = Query(..., description="Maximum longitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    kategori: Optional[str] = Query(None, description="Filter by kategori_kemiskinan"),
    db: Session = Depends(get_db)
):
    """
    Get santri within bounding box.
    
    **Use Case:**
    - Get santri visible in map viewport
    - Optimize map loading
    
    **Example:**
    ```
    GET /api/santri-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2
    ```
    """
    try:
        service = SantriMapService(db)
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
                result = db.execute(text(f"SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM santri_map WHERE id = '{r.id}'")).first()
                if result:
                    data.append({
                        "id": str(r.id),
                        "santri_id": str(r.santri_id),
                        "nama": r.nama,
                        "skor_terakhir": r.skor_terakhir,
                        "kategori_kemiskinan": r.kategori_kemiskinan,
                        "latitude": result.lat,
                        "longitude": result.lon
                    })
        
        return success_response(data=data, message=f"Found {len(data)} santri")
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/statistics", response_model=None)
def get_santri_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about santri map data.
    
    **Returns:**
    - Total santri
    - Santri with/without location
    - Count by poverty category
    """
    try:
        service = SantriMapService(db)
        stats = service.get_statistics()
        return success_response(data=stats, message="Statistics retrieved successfully")
    except Exception as e:
        return error_response(message=str(e), status_code=500)
