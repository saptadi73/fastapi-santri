"""Service for Pesantren Map operations."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_AsGeoJSON

from app.models.pesantren_map import PesantrenMap
from app.models.pondok_pesantren import PondokPesantren


class PesantrenMapService:
    """Service for managing pesantren map data."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upsert_from_scoring(
        self,
        pesantren_id: UUID,
        skor_total: int,
        kategori_kelayakan: str
    ) -> PesantrenMap:
        """
        Insert or update pesantren map when scoring is calculated.
        
        Args:
            pesantren_id: UUID of pesantren
            skor_total: Latest total score
            kategori_kelayakan: Quality category
            
        Returns:
            PesantrenMap record
        """
        # Get pesantren data
        pesantren = self.db.query(PondokPesantren).filter(
            PondokPesantren.id == pesantren_id
        ).first()
        
        if not pesantren:
            raise ValueError(f"Pesantren with id {pesantren_id} not found")
        
        # Check if map record exists
        existing: PesantrenMap | None = self.db.query(PesantrenMap).filter(
            PesantrenMap.pesantren_id == pesantren_id
        ).first()
        
        # Use existing lokasi geometry from pesantren (already a POINT)
        lokasi = getattr(pesantren, 'lokasi', None)
        
        if existing:
            # Update existing record
            existing.nama = pesantren.nama  # type: ignore
            existing.nsp = pesantren.nsp  # type: ignore
            existing.skor_terakhir = skor_total  # type: ignore
            existing.kategori_kelayakan = kategori_kelayakan  # type: ignore
            existing.kabupaten = pesantren.kabupaten  # type: ignore
            existing.provinsi = pesantren.provinsi  # type: ignore
            existing.jumlah_santri = pesantren.jumlah_santri  # type: ignore
            existing.lokasi = lokasi  # type: ignore
            
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new record
            new_map = PesantrenMap(
                pesantren_id=pesantren_id,
                nama=pesantren.nama,
                nsp=pesantren.nsp,
                skor_terakhir=skor_total,
                kategori_kelayakan=kategori_kelayakan,
                kabupaten=pesantren.kabupaten,
                provinsi=pesantren.provinsi,
                jumlah_santri=pesantren.jumlah_santri,
                lokasi=lokasi
            )
            self.db.add(new_map)
            self.db.commit()
            self.db.refresh(new_map)
            return new_map
    
    def get_all_geojson(
        self,
        kategori: Optional[str] = None,
        provinsi: Optional[str] = None,
        kabupaten: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get all pesantren as GeoJSON FeatureCollection.
        
        Args:
            kategori: Filter by kategori_kelayakan
            provinsi: Filter by provinsi
            kabupaten: Filter by kabupaten
            limit: Maximum records to return
            
        Returns:
            GeoJSON FeatureCollection
        """
        query = self.db.query(PesantrenMap).filter(PesantrenMap.lokasi.isnot(None))
        
        if kategori:
            query = query.filter(PesantrenMap.kategori_kelayakan == kategori)
        
        if provinsi:
            query = query.filter(PesantrenMap.provinsi == provinsi)
        
        if kabupaten:
            query = query.filter(PesantrenMap.kabupaten == kabupaten)
        
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
                        "pesantren_id": str(record.pesantren_id),
                        "nama": record.nama,
                        "nsp": record.nsp,
                        "skor_terakhir": record.skor_terakhir,
                        "kategori_kelayakan": record.kategori_kelayakan,
                        "kabupaten": record.kabupaten,
                        "provinsi": record.provinsi,
                        "jumlah_santri": record.jumlah_santri
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
    ) -> List[PesantrenMap]:
        """
        Get pesantren within bounding box.
        
        Args:
            min_lon: Minimum longitude
            min_lat: Minimum latitude
            max_lon: Maximum longitude
            max_lat: Maximum latitude
            kategori: Filter by kategori_kelayakan
            
        Returns:
            List of PesantrenMap records
        """
        bbox_wkt = f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
        
        query = self.db.query(PesantrenMap).filter(
            PesantrenMap.lokasi.isnot(None),
            func.ST_Within(
                PesantrenMap.lokasi,
                func.ST_GeomFromText(bbox_wkt, 4326)
            )
        )
        
        if kategori:
            query = query.filter(PesantrenMap.kategori_kelayakan == kategori)
        
        return query.all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pesantren map data.
        
        Returns:
            Dictionary with statistics
        """
        total = self.db.query(func.count(PesantrenMap.id)).scalar()
        with_location = self.db.query(func.count(PesantrenMap.id)).filter(
            PesantrenMap.lokasi.isnot(None)
        ).scalar()
        
        # Count by category
        categories = self.db.query(
            PesantrenMap.kategori_kelayakan,
            func.count(PesantrenMap.id)
        ).group_by(PesantrenMap.kategori_kelayakan).all()
        
        return {
            "total_pesantren": total,
            "with_location": with_location,
            "without_location": total - with_location,
            "by_category": {cat: count for cat, count in categories}
        }
