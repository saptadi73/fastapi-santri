"""Service for Santri Map operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_AsGeoJSON, ST_MakePoint, ST_SetSRID

from app.models.santri_map import SantriMap
from app.models.santri_pribadi import SantriPribadi


class SantriMapService:
    """Service for managing santri map data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upsert_from_scoring(
        self,
        santri_id: UUID,
        skor_total: int,
        kategori_kemiskinan: str
    ) -> SantriMap:
        """
        Insert or update santri map when scoring is calculated.
        
        Args:
            santri_id: UUID of santri
            skor_total: Latest total score
            kategori_kemiskinan: Poverty category
            
        Returns:
            SantriMap record
        """
        # Get santri pribadi data
        santri = self.db.query(SantriPribadi).filter(SantriPribadi.id == santri_id).first()
        if not santri:
            raise ValueError(f"Santri with id {santri_id} not found")
        
        # Get lokasi safely (might not exist on model)
        lokasi = getattr(santri, 'lokasi', None)
        
        # Check if map record exists
        existing: SantriMap | None = self.db.query(SantriMap).filter(SantriMap.santri_id == santri_id).first()
        
        if existing:
            # Update existing record
            existing.nama = santri.nama  # type: ignore
            existing.skor_terakhir = skor_total  # type: ignore
            existing.kategori_kemiskinan = kategori_kemiskinan  # type: ignore
            existing.pesantren_id = santri.pesantren_id  # type: ignore
            
            # Update location if santri has lokasi
            if lokasi is not None:
                existing.lokasi = lokasi  # type: ignore
            
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new record
            new_map = SantriMap(
                santri_id=santri_id,
                nama=santri.nama,
                skor_terakhir=skor_total,
                kategori_kemiskinan=kategori_kemiskinan,
                pesantren_id=santri.pesantren_id,
                lokasi=lokasi
            )
            self.db.add(new_map)
            self.db.commit()
            self.db.refresh(new_map)
            return new_map
    
    def get_all_geojson(
        self,
        kategori: Optional[str] = None,
        pesantren_id: Optional[UUID] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get all santri as GeoJSON FeatureCollection.
        
        Args:
            kategori: Filter by kategori_kemiskinan
            pesantren_id: Filter by pesantren
            limit: Maximum records to return
            
        Returns:
            GeoJSON FeatureCollection
        """
        query = self.db.query(SantriMap).filter(SantriMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(SantriMap.kategori_kemiskinan == kategori)
        
        if pesantren_id:
            query = query.filter(SantriMap.pesantren_id == pesantren_id)
        
        query = query.limit(limit)
        records = query.all()
        
        features = []
        for record in records:
            # Get geometry as GeoJSON
            geom_json = self.db.scalar(
                func.ST_AsGeoJSON(record.lokasi)
            )
            
            if geom_json:
                import json
                geometry = json.loads(geom_json)
                
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "id": str(record.id),
                        "santri_id": str(record.santri_id),
                        "nama": record.nama,
                        "skor_terakhir": record.skor_terakhir,
                        "kategori_kemiskinan": record.kategori_kemiskinan,
                        "pesantren_id": str(record.pesantren_id) if record.pesantren_id is not None else None
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "total": len(features)
        }
    
    def get_by_bounding_box(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        kategori: Optional[str] = None
    ) -> List[SantriMap]:
        """
        Get santri within bounding box.
        
        Args:
            min_lon: Minimum longitude
            min_lat: Minimum latitude
            max_lon: Maximum longitude
            max_lat: Maximum latitude
            kategori: Filter by kategori_kemiskinan
            
        Returns:
            List of SantriMap records
        """
        # Create bounding box polygon
        bbox_wkt = f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
        
        query = self.db.query(SantriMap).filter(
            SantriMap.lokasi.isnot(None),
            func.ST_Within(
                SantriMap.lokasi,
                func.ST_GeomFromText(bbox_wkt, 4326)
            )
        )
        
        if kategori:
            query = query.filter(SantriMap.kategori_kemiskinan == kategori)
        
        return query.all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about santri map data.
        
        Returns:
            Dictionary with statistics
        """
        total = self.db.query(func.count(SantriMap.id)).scalar()
        with_location = self.db.query(func.count(SantriMap.id)).filter(
            SantriMap.lokasi.isnot(None)
        ).scalar()
        
        # Count by category
        categories = self.db.query(
            SantriMap.kategori_kemiskinan,
            func.count(SantriMap.id)
        ).group_by(SantriMap.kategori_kemiskinan).all()
        
        return {
            "total_santri": total,
            "with_location": with_location,
            "without_location": total - with_location,
            "by_category": {cat: count for cat, count in categories}
        }
