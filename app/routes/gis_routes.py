"""GIS endpoints optimized for frontend visualization."""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.database import get_db
from app.models.santri_map import SantriMap
from app.models.pesantren_map import PesantrenMap
from app.supports import success_response, error_response

router = APIRouter(prefix="/gis", tags=["GIS"])


@router.get("/santri-points")
def get_santri_points(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kemiskinan"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren_id"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """
    Get santri locations as simple points for frontend map.
    
    Returns array of points with coordinates and basic info.
    Optimized for fast frontend rendering.
    """
    try:
        query = db.query(SantriMap).filter(SantriMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(SantriMap.kategori_kemiskinan == kategori)
        if pesantren_id:
            query = query.filter(SantriMap.pesantren_id == pesantren_id)
        
        records = query.limit(limit).all()
        
        points = []
        for record in records:
            # Extract coordinates
            result = db.execute(
                text("SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM santri_map WHERE id = :id"),
                {"id": record.id}
            ).first()
            
            if result:
                pesantren_id_val = getattr(record, "pesantren_id", None)
                points.append({
                    "id": str(record.id),
                    "name": record.nama,
                    "lat": result.lat,
                    "lon": result.lon,
                    "category": record.kategori_kemiskinan,
                    "score": record.skor_terakhir,
                    "pesantren_id": str(pesantren_id_val) if pesantren_id_val is not None else None
                })
        
        # Build valid GeoJSON FeatureCollection
        features = []
        for point in points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                },
                "properties": {
                    "id": point["id"],
                    "name": point["name"],
                    "category": point["category"],
                    "score": point["score"],
                    "pesantren_id": point["pesantren_id"]
                }
            })
        
        return success_response(
            data={
                "type": "FeatureCollection",
                "features": features,
                "total": len(features)
            },
            message=f"Retrieved {len(features)} santri locations"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/pesantren-points")
def get_pesantren_points(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kelayakan"),
    provinsi: Optional[str] = Query(None, description="Filter by provinsi"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """
    Get pesantren locations as simple points for frontend map.
    
    Returns array of points with coordinates and basic info.
    Optimized for fast frontend rendering.
    """
    try:
        query = db.query(PesantrenMap).filter(PesantrenMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(PesantrenMap.kategori_kelayakan == kategori)
        if provinsi:
            query = query.filter(PesantrenMap.provinsi == provinsi)
        
        records = query.limit(limit).all()
        
        points = []
        for record in records:
            # Extract coordinates
            result = db.execute(
                text("SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM pesantren_map WHERE id = :id"),
                {"id": record.id}
            ).first()
            
            if result:
                points.append({
                    "id": str(record.id),
                    "name": record.nama,
                    "nsp": record.nsp,
                    "lat": result.lat,
                    "lon": result.lon,
                    "category": record.kategori_kelayakan,
                    "score": record.skor_terakhir,
                    "province": record.provinsi,
                    "regency": record.kabupaten,
                    "students": record.jumlah_santri
                })
        
        # Build valid GeoJSON FeatureCollection
        features = []
        for point in points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                },
                "properties": {
                    "id": point["id"],
                    "name": point["name"],
                    "nsp": point["nsp"],
                    "category": point["category"],
                    "score": point["score"],
                    "province": point["province"],
                    "regency": point["regency"],
                    "students": point["students"]
                }
            })
        
        return success_response(
            data={
                "type": "FeatureCollection",
                "features": features,
                "total": len(features)
            },
            message=f"Retrieved {len(features)} pesantren locations"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/heatmap")
def get_santri_heatmap(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kemiskinan"),
    db: Session = Depends(get_db)
):
    """
    Get santri heatmap data for density visualization.
    
    Returns points with intensity/weight for heatmap overlay.
    Weight = score (higher score = higher poverty = higher intensity).
    """
    try:
        query = db.query(SantriMap).filter(SantriMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(SantriMap.kategori_kemiskinan == kategori)
        
        records = query.all()
        
        # Category to intensity mapping
        category_weight = {
            "Sangat Miskin": 1.0,
            "Miskin": 0.75,
            "Rentan": 0.5,
            "Tidak Miskin": 0.25
        }
        
        points = []
        for record in records:
            result = db.execute(
                text("SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM santri_map WHERE id = :id"),
                {"id": record.id}
            ).first()
            
            if result:
                raw_score = getattr(record, "skor_terakhir", None)
                score_val = float(raw_score) if isinstance(raw_score, (int, float)) else 0.0
                raw_category = getattr(record, "kategori_kemiskinan", None)
                kategori_val = raw_category if isinstance(raw_category, str) else ""
                # Intensity = normalized score (0-100) + category weight
                intensity_raw = (score_val / 100.0) * category_weight.get(kategori_val, 0.5)
                intensity = min(intensity_raw, 1.0)
                
                points.append({
                    "lat": result.lat,
                    "lon": result.lon,
                    "intensity": min(intensity, 1.0),  # Cap at 1.0
                    "value": record.skor_terakhir,
                    "category": record.kategori_kemiskinan
                })
        
        # Build valid GeoJSON FeatureCollection with intensity properties
        features = []
        for point in points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                },
                "properties": {
                    "intensity": point["intensity"],
                    "value": point["value"],
                    "category": point["category"]
                }
            })
        
        return success_response(
            data={
                "type": "FeatureCollection",
                "features": features,
                "total": len(features),
                "intensity_min": 0,
                "intensity_max": 1.0
            },
            message=f"Generated heatmap with {len(features)} santri points"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/pesantren-heatmap")
def get_pesantren_heatmap(
    kategori: Optional[str] = Query(None, description="Filter by kategori_kelayakan"),
    db: Session = Depends(get_db)
):
    """
    Get pesantren heatmap data for quality/density visualization.
    
    Returns points with intensity/weight for heatmap overlay.
    Weight = score (higher score = better quality = higher intensity).
    """
    try:
        query = db.query(PesantrenMap).filter(PesantrenMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(PesantrenMap.kategori_kelayakan == kategori)
        
        records = query.all()
        
        # Category to intensity mapping (inverse of santri - higher score = better)
        category_weight = {
            "sangat_layak": 1.0,
            "layak": 0.75,
            "cukup_layak": 0.5,
            "tidak_layak": 0.25
        }
        
        points = []
        for record in records:
            result = db.execute(
                text("SELECT ST_X(lokasi) as lon, ST_Y(lokasi) as lat FROM pesantren_map WHERE id = :id"),
                {"id": record.id}
            ).first()
            
            if result:
                raw_score = getattr(record, "skor_terakhir", None)
                score_val = float(raw_score) if isinstance(raw_score, (int, float)) else 0.0
                raw_category = getattr(record, "kategori_kelayakan", None)
                kategori_val = raw_category if isinstance(raw_category, str) else ""
                # Intensity = normalized score (0-100) + category weight
                intensity_raw = (score_val / 100.0) * category_weight.get(kategori_val, 0.5)
                intensity = min(intensity_raw, 1.0)
                
                points.append({
                    "lat": result.lat,
                    "lon": result.lon,
                    "intensity": min(intensity, 1.0),  # Cap at 1.0
                    "value": record.skor_terakhir,
                    "category": record.kategori_kelayakan,
                    "name": record.nama,
                    "province": record.provinsi
                })
        
        # Build valid GeoJSON FeatureCollection with intensity properties
        features = []
        for point in points:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                },
                "properties": {
                    "intensity": point["intensity"],
                    "value": point["value"],
                    "category": point["category"],
                    "name": point["name"],
                    "province": point["province"]
                }
            })
        
        return success_response(
            data={
                "type": "FeatureCollection",
                "features": features,
                "total": len(features),
                "intensity_min": 0,
                "intensity_max": 1.0
            },
            message=f"Generated heatmap with {len(features)} pesantren points"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)
