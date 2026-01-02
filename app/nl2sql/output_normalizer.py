"""Output Normalizer untuk NL2SQL - Normalisasi hasil query."""

import json
from typing import Any, List, Dict, Union, Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from app.nl2sql.geojson_generator import GeoJSONGenerator


class OutputNormalizer:
    """Normalisasi output dari database queries ke format konsisten."""
    
    @staticmethod
    def normalize_value(value: Any) -> Any:
        """Normalisasi nilai individual."""
        if value is None:
            return None
        
        # Handle datetime
        if isinstance(value, datetime):
            return value.isoformat()
        
        # Handle date
        if isinstance(value, date):
            return value.isoformat()
        
        # Handle Decimal
        if isinstance(value, Decimal):
            return float(value)
        
        # Handle UUID
        if isinstance(value, UUID):
            return str(value)
        
        # Handle bytes
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except:
                return str(value)
        
        # Handle dict/list recursively
        if isinstance(value, dict):
            return {k: OutputNormalizer.normalize_value(v) for k, v in value.items()}
        
        if isinstance(value, (list, tuple)):
            return [OutputNormalizer.normalize_value(v) for v in value]
        
        return value
    
    @staticmethod
    def normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalisasi list dari rows database ke format JSON-safe.
        
        Args:
            rows: List dari dict rows dari database
            
        Returns:
            List dari normalized dict rows
        """
        if not rows:
            return []
        
        normalized = []
        for row in rows:
            if isinstance(row, dict):
                normalized_row = {
                    key: OutputNormalizer.normalize_value(value)
                    for key, value in row.items()
                }
            else:
                # Jika row adalah object, convert ke dict dulu
                normalized_row = OutputNormalizer.normalize_value(row)
            
            normalized.append(normalized_row)
        
        return normalized
    
    @staticmethod
    def normalize_single_value(value: Any) -> Any:
        """Normalisasi single value (untuk aggregates seperti COUNT)."""
        return OutputNormalizer.normalize_value(value)
    
    @staticmethod
    def format_for_response(
        rows: Union[List[Dict[str, Any]], Any],
        intent: str,
        include_count: bool = False,
        center_latitude: Optional[float] = None,
        center_longitude: Optional[float] = None
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Format output berdasarkan intent type.
        
        Args:
            rows: Data dari database
            intent: Intent type (list, count, statistics, etc)
            include_count: Include row count dalam response
            center_latitude: Center latitude untuk distance queries
            center_longitude: Center longitude untuk distance queries
            
        Returns:
            Formatted response
        """
        if intent == "count":
            # Untuk COUNT, return single value
            if isinstance(rows, list) and len(rows) > 0:
                first_row = rows[0]
                if isinstance(first_row, dict):
                    # Cari field yang berisi count
                    count_value = first_row.get("total") or first_row.get("count") or first_row.get("COUNT(*)")
                    return {
                        "total": OutputNormalizer.normalize_value(count_value),
                        "count": OutputNormalizer.normalize_value(count_value)
                    }
            return {"total": 0, "count": 0}
        
        elif intent == "statistics":
            # Untuk STATISTICS, return normalized rows dengan summary
            normalized = OutputNormalizer.normalize_rows(rows if isinstance(rows, list) else [rows])
            return {
                "data": normalized,
                "row_count": len(normalized) if normalized else 0
            }
        
        elif intent in ["ranking", "list", "filter"]:
            # Untuk LIST/FILTER/RANKING, return normalized rows
            normalized = OutputNormalizer.normalize_rows(rows if isinstance(rows, list) else [rows])
            
            response = {"data": normalized, "count": len(normalized)}
            
            return response
        
        elif intent in ["location", "heatmap"]:
            # Untuk LOCATION/HEATMAP, return dengan GIS fields sebagai GeoJSON
            normalized = OutputNormalizer.normalize_rows(rows if isinstance(rows, list) else [rows])
            
            # Check if ada heatmap intent dengan intensity field
            if intent == "heatmap":
                # Cari intensity/skor field
                intensity_field = None
                if normalized and isinstance(normalized[0], dict):
                    for field in ["intensity", "skor", "score", "nilai", "weight"]:
                        if field in normalized[0]:
                            intensity_field = field
                            break
                
                # Generate heatmap GeoJSON
                return OutputNormalizer._normalize_value(
                    GeoJSONGenerator.rows_to_heatmap_geojson(
                        rows=normalized,
                        lat_field="latitude",
                        lon_field="longitude",
                        intensity_field=intensity_field
                    )
                )
            else:  # location intent
                # Generate standard GeoJSON
                return OutputNormalizer._normalize_value(
                    GeoJSONGenerator.rows_to_geojson(
                        rows=normalized,
                        lat_field="latitude",
                        lon_field="longitude",
                        id_field="id"
                    )
                )
        
        elif intent == "distance":
            # Untuk DISTANCE, return dengan GeoJSON + distance field
            normalized = OutputNormalizer.normalize_rows(rows if isinstance(rows, list) else [rows])
            
            # Sort by distance jika ada
            if normalized and isinstance(normalized[0], dict) and "distance" in normalized[0]:
                normalized = sorted(normalized, key=lambda x: x.get("distance", float('inf')))
            
            # Use provided center or extract from data
            use_center_lat = center_latitude
            use_center_lon = center_longitude
            
            # If no center provided, try to extract dari data
            if use_center_lat is None or use_center_lon is None:
                if normalized and isinstance(normalized[0], dict):
                    use_center_lat = use_center_lat or normalized[0].get("center_latitude", 0)
                    use_center_lon = use_center_lon or normalized[0].get("center_longitude", 0)
            
            # Default if still None
            use_center_lat = use_center_lat or 0
            use_center_lon = use_center_lon or 0
            
            # Generate GeoJSON dengan distance
            return OutputNormalizer._normalize_value(
                GeoJSONGenerator.rows_to_geojson_with_distance(
                    rows=normalized,
                    center_latitude=use_center_lat,
                    center_longitude=use_center_lon,
                    lat_field="latitude",
                    lon_field="longitude",
                    distance_field="distance"
                )
            )
        
        else:  # Default untuk UNKNOWN, HELP, etc
            normalized = OutputNormalizer.normalize_rows(rows if isinstance(rows, list) else [rows])
            return {
                "data": normalized,
                "count": len(normalized)
            }
    
    @staticmethod
    def clean_field_names(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean field names (remove underscores, convert to camelCase jika diperlukan).
        
        Args:
            rows: List dari dict rows
            
        Returns:
            Rows dengan cleaned field names
        """
        if not rows:
            return []
        
        cleaned = []
        for row in rows:
            if isinstance(row, dict):
                cleaned_row = {}
                for key, value in row.items():
                    # Convert snake_case ke camelCase (optional)
                    # cleaned_key = OutputNormalizer._snake_to_camel(key)
                    # Untuk sekarang, keep original key
                    cleaned_row[key] = value
                cleaned.append(cleaned_row)
            else:
                cleaned.append(row)
        
        return cleaned
    
    @staticmethod
    def _snake_to_camel(snake_str: str) -> str:
        """Convert snake_case ke camelCase."""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def validate_json_serializable(obj: Any) -> bool:
        """Check if object dapat di-serialize ke JSON."""
        try:
            json.dumps(OutputNormalizer.normalize_value(obj))
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def _normalize_value(obj: Any) -> Any:
        """Helper untuk normalize nested objects (for GeoJSON)."""
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        if isinstance(obj, dict):
            return {k: OutputNormalizer._normalize_value(v) for k, v in obj.items()}
        
        if isinstance(obj, (list, tuple)):
            return [OutputNormalizer._normalize_value(v) for v in obj]
        
        return OutputNormalizer.normalize_value(obj)
    
    @staticmethod
    def export_geojson(geojson_data: Dict[str, Any], pretty: bool = True) -> str:
        """Export GeoJSON ke JSON string."""
        try:
            if pretty:
                return json.dumps(geojson_data, indent=2, default=str)
            else:
                return json.dumps(geojson_data, default=str)
        except (TypeError, ValueError) as e:
            return json.dumps({
                "error": f"Failed to serialize GeoJSON: {str(e)}",
                "type": "FeatureCollection",
                "features": []
            })
    
    @staticmethod
    def validate_geojson_structure(geojson_data: Dict[str, Any]) -> bool:
        """Validasi struktur GeoJSON RFC 7946."""
        # Check minimum requirements
        if not isinstance(geojson_data, dict):
            return False
        
        required_fields = ["type", "features"]
        if not all(field in geojson_data for field in required_fields):
            return False
        
        if geojson_data["type"] != "FeatureCollection":
            return False
        
        if not isinstance(geojson_data["features"], list):
            return False
        
        # Validate each feature
        for feature in geojson_data["features"]:
            if not isinstance(feature, dict):
                return False
            if not all(k in feature for k in ["type", "geometry", "properties"]):
                return False
            if feature["type"] != "Feature":
                return False
            if not isinstance(feature["geometry"], dict):
                return False
            if "type" not in feature["geometry"]:
                return False
        
        return True
    
    @staticmethod
    def add_metadata_to_geojson(geojson_data: Dict[str, Any], 
                                intent: Optional[str] = None,
                                query: Optional[str] = None,
                                count: Optional[int] = None) -> Dict[str, Any]:
        """Tambahkan metadata ke GeoJSON response."""
        if "properties" not in geojson_data:
            geojson_data["properties"] = {}
        
        if intent:
            geojson_data["properties"]["intent"] = intent
        if query:
            geojson_data["properties"]["query"] = query
        if count is not None:
            geojson_data["properties"]["total_features"] = count
        
        # Always add timestamp
        geojson_data["properties"]["generated_at"] = datetime.now().isoformat()
        
        return geojson_data
