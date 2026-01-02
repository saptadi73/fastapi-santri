"""GeoJSON Generator untuk NL2SQL - Generate GeoJSON untuk map visualization."""

from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
from datetime import datetime


class GeoJSONGenerator:
    """Generate GeoJSON dari database query results untuk map integration."""
    
    @staticmethod
    def create_feature(
        properties: Dict[str, Any],
        latitude: float,
        longitude: float,
        feature_id: Optional[str] = None,
        geometry_type: str = "Point"
    ) -> Dict[str, Any]:
        """
        Create GeoJSON Feature.
        
        Args:
            properties: Feature properties
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            feature_id: Optional feature ID
            geometry_type: Geometry type (Point, LineString, Polygon)
            
        Returns:
            GeoJSON Feature object
        """
        feature = {
            "type": "Feature",
            "geometry": {
                "type": geometry_type,
                "coordinates": [longitude, latitude]  # GeoJSON uses [lon, lat]
            },
            "properties": properties
        }
        
        if feature_id:
            feature["id"] = feature_id
        
        return feature
    
    @staticmethod
    def create_feature_collection(
        features: List[Dict[str, Any]],
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create GeoJSON FeatureCollection.
        
        Args:
            features: List of GeoJSON features
            properties: Optional collection-level properties
            
        Returns:
            GeoJSON FeatureCollection
        """
        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }
        
        if properties:
            feature_collection["properties"] = properties
        
        return feature_collection
    
    @staticmethod
    def rows_to_geojson(
        rows: List[Dict[str, Any]],
        lat_field: str = "latitude",
        lon_field: str = "longitude",
        id_field: Optional[str] = None,
        exclude_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convert database rows to GeoJSON FeatureCollection.
        
        Args:
            rows: List dari dict rows (harus punya lat/lon fields)
            lat_field: Field name untuk latitude (default: "latitude")
            lon_field: Field name untuk longitude (default: "longitude")
            id_field: Field name untuk feature ID (optional)
            exclude_fields: Fields to exclude dari properties
            
        Returns:
            GeoJSON FeatureCollection
        """
        if not rows:
            return GeoJSONGenerator.create_feature_collection([])
        
        if exclude_fields is None:
            exclude_fields = []
        
        # Always exclude geometry fields dari properties
        exclude_fields.extend([lat_field, lon_field])
        if id_field:
            exclude_fields.append(id_field)
        
        features = []
        for row in rows:
            # Extract coordinates
            latitude = row.get(lat_field)
            longitude = row.get(lon_field)
            
            if latitude is None or longitude is None:
                continue  # Skip rows without coordinates
            
            # Convert to float
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (TypeError, ValueError):
                continue
            
            # Build properties (exclude geometry fields)
            properties = {
                key: GeoJSONGenerator._serialize_value(value)
                for key, value in row.items()
                if key not in exclude_fields
            }
            
            # Get feature ID
            feature_id = row.get(id_field) if id_field else None
            
            # Create feature
            feature = GeoJSONGenerator.create_feature(
                properties=properties,
                latitude=latitude,
                longitude=longitude,
                feature_id=str(feature_id) if feature_id else None
            )
            
            features.append(feature)
        
        return GeoJSONGenerator.create_feature_collection(
            features=features,
            properties={
                "count": len(features),
                "generated_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def rows_to_geojson_with_distance(
        rows: List[Dict[str, Any]],
        center_latitude: float,
        center_longitude: float,
        lat_field: str = "latitude",
        lon_field: str = "longitude",
        distance_field: str = "distance",
        id_field: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert rows to GeoJSON dengan distance dari center point.
        
        Args:
            rows: Database rows
            center_latitude: Center point latitude
            center_longitude: Center point longitude
            lat_field: Latitude field name
            lon_field: Longitude field name
            distance_field: Field name untuk distance value
            id_field: Optional ID field
            
        Returns:
            GeoJSON dengan distance properties
        """
        geojson = GeoJSONGenerator.rows_to_geojson(
            rows=rows,
            lat_field=lat_field,
            lon_field=lon_field,
            id_field=id_field,
            exclude_fields=[distance_field]
        )
        
        # Add center point as feature
        center_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [center_longitude, center_latitude]
            },
            "properties": {
                "type": "center",
                "name": "Center Point"
            }
        }
        
        geojson["features"].insert(0, center_feature)
        
        # Update count
        if "properties" not in geojson:
            geojson["properties"] = {}
        geojson["properties"]["center"] = {
            "latitude": center_latitude,
            "longitude": center_longitude
        }
        
        return geojson
    
    @staticmethod
    def rows_to_heatmap_geojson(
        rows: List[Dict[str, Any]],
        lat_field: str = "latitude",
        lon_field: str = "longitude",
        intensity_field: Optional[str] = None,
        intensity_range: tuple = (0, 100)
    ) -> Dict[str, Any]:
        """
        Convert rows to GeoJSON untuk heatmap visualization.
        
        Args:
            rows: Database rows dengan lat/lon
            lat_field: Latitude field
            lon_field: Longitude field
            intensity_field: Field untuk intensity value (0-1)
            intensity_range: Min/max untuk intensity normalization
            
        Returns:
            GeoJSON dengan intensity properties untuk heatmap
        """
        if not rows:
            return GeoJSONGenerator.create_feature_collection([])
        
        exclude_fields = [lat_field, lon_field]
        if intensity_field:
            exclude_fields.append(intensity_field)
        
        features = []
        min_intensity, max_intensity = intensity_range
        
        for row in rows:
            latitude = row.get(lat_field)
            longitude = row.get(lon_field)
            
            if latitude is None or longitude is None:
                continue
            
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (TypeError, ValueError):
                continue
            
            # Get intensity
            if intensity_field and isinstance(row, dict):
                intensity = row.get(intensity_field, 0.5)
            else:
                intensity = 0.5
            try:
                intensity = float(intensity)
                # Normalize to 0-1 range
                if max_intensity != min_intensity:
                    intensity = (intensity - min_intensity) / (max_intensity - min_intensity)
                intensity = max(0, min(1, intensity))
            except (TypeError, ValueError):
                intensity = 0.5
            
            # Build properties
            properties = {
                key: GeoJSONGenerator._serialize_value(value)
                for key, value in row.items()
                if key not in exclude_fields
            }
            properties["intensity"] = intensity
            
            feature = GeoJSONGenerator.create_feature(
                properties=properties,
                latitude=latitude,
                longitude=longitude
            )
            
            features.append(feature)
        
        return GeoJSONGenerator.create_feature_collection(
            features=features,
            properties={
                "count": len(features),
                "heatmap": True,
                "intensity_range": [min_intensity, max_intensity]
            }
        )
    
    @staticmethod
    def create_circle_feature(
        center_latitude: float,
        center_longitude: float,
        radius_km: float,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create GeoJSON circle feature (untuk radius visualization).
        
        Args:
            center_latitude: Center latitude
            center_longitude: Center longitude
            radius_km: Radius dalam kilometer
            properties: Feature properties
            
        Returns:
            GeoJSON circle feature (as Point with radius property)
        """
        if properties is None:
            properties = {}
        
        properties["radius_km"] = radius_km
        properties["type"] = "radius_circle"
        
        return GeoJSONGenerator.create_feature(
            properties=properties,
            latitude=center_latitude,
            longitude=center_longitude,
            feature_id="radius_circle"
        )
    
    @staticmethod
    def create_bounding_box(
        features: List[Dict[str, Any]]
    ) -> Optional[List[float]]:
        """
        Calculate bounding box dari features.
        
        Args:
            features: List of GeoJSON features
            
        Returns:
            [minLon, minLat, maxLon, maxLat] atau None jika kosong
        """
        if not features:
            return None
        
        min_lon = float('inf')
        min_lat = float('inf')
        max_lon = float('-inf')
        max_lat = float('-inf')
        
        for feature in features:
            if feature.get("type") != "Feature":
                continue
            
            geometry = feature.get("geometry", {})
            if geometry.get("type") != "Point":
                continue
            
            coords = geometry.get("coordinates", [])
            if len(coords) < 2:
                continue
            
            lon, lat = coords[0], coords[1]
            
            min_lon = min(min_lon, lon)
            min_lat = min(min_lat, lat)
            max_lon = max(max_lon, lon)
            max_lat = max(max_lat, lat)
        
        if min_lon == float('inf'):
            return None
        
        return [min_lon, min_lat, max_lon, max_lat]
    
    @staticmethod
    def add_properties_to_geojson(
        geojson: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Add additional properties ke GeoJSON."""
        if "properties" not in geojson:
            geojson["properties"] = {}
        
        geojson["properties"].update(kwargs)
        return geojson
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize value ke JSON-compatible type."""
        if value is None:
            return None
        
        if isinstance(value, (str, int, float, bool)):
            return value
        
        if isinstance(value, Decimal):
            return float(value)
        
        if isinstance(value, datetime):
            return value.isoformat()
        
        if isinstance(value, dict):
            return {k: GeoJSONGenerator._serialize_value(v) for k, v in value.items()}
        
        if isinstance(value, (list, tuple)):
            return [GeoJSONGenerator._serialize_value(v) for v in value]
        
        return str(value)
