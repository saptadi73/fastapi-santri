"""API endpoints for NL2SQL with Intent Detection."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.nl2sql.intent_classifier import IntentClassifier, IntentType
from app.nl2sql.nl2sql_service import NL2SQLService
from app.supports import success_response, error_response

router = APIRouter(prefix="/nl2sql", tags=["AI Query"])


class IntentDetectionRequest(BaseModel):
    """Request for intent detection."""
    query: str


class IntentDetectionResponse(BaseModel):
    """Response from intent detection."""
    intent: str
    confidence: float
    keywords: list[str]
    entity_types: list[str]
    description: str


class NL2SQLRequest(BaseModel):
    """Request for NL2SQL query."""
    query: str
    explain: bool = False  # Return explanation of generated SQL


class NL2SQLResponse(BaseModel):
    """Response from NL2SQL query."""
    intent: str
    confidence: float
    sql_query: str
    result: list | dict
    geojson: Optional[dict] = None  # GeoJSON output for location intents
    execution_time_ms: float
    error: Optional[str] = None


class GeoJSONMapResponse(BaseModel):
    """Response with GeoJSON for map visualization."""
    type: str = "FeatureCollection"
    features: list[dict]
    properties: dict
    bbox: Optional[list[float]] = None


@router.post("/detect-intent", response_model=dict)
def detect_intent(request: IntentDetectionRequest):
    """
    Detect intent of user query.
    
    Example:
    - "Tunjukkan semua santri" → LIST intent
    - "Berapa jumlah santri?" → COUNT intent
    - "Pesantren mana terbaik?" → RANKING intent
    
    Request body:
    ```json
    {
      "query": "Tunjukkan santri dengan score tertinggi"
    }
    ```
    
    Response:
    ```json
    {
      "success": true,
      "data": {
        "intent": "ranking",
        "confidence": 0.85,
        "keywords": ["tunjukkan", "tertinggi"],
        "entity_types": ["santri", "score"],
        "description": "User menanyakan tentang ranking untuk santri, score"
      }
    }
    ```
    """
    try:
        classifier = IntentClassifier()
        result = classifier.classify(request.query)
        
        return success_response(
            data={
                "intent": result.intent.value,
                "confidence": round(result.confidence, 2),
                "keywords": result.keywords,
                "entity_types": result.entity_types,
                "description": result.description
            },
            message="Intent terdeteksi"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.post("/query", response_model=dict)
def nl2sql_query(
    request: NL2SQLRequest,
    db: Session = Depends(get_db)
):
    """
    Convert AI query to SQL and execute query.
    
    Example:
    - "Tunjukkan 10 santri dengan skor tertinggi di Jawa Barat"
    - "Berapa jumlah santri yang masuk kategori sangat miskin?"
    - "Heatmap distribusi santri kemiskinan di Bandung"
    
    Request body:
    ```json
    {
      "query": "Tunjukkan santri miskin di Jawa Barat",
      "explain": true
    }
    ```
    
    Response:
    ```json
    {
      "success": true,
      "data": {
        "intent": "filter",
        "confidence": 0.92,
        "sql_query": "SELECT * FROM santri_pribadi WHERE kategori_kemiskinan = 'Miskin' AND provinsi = 'Jawa Barat' LIMIT 1000",
        "result": [...],
        "execution_time_ms": 125.5
      }
    }
    ```
    """
    try:
        service = NL2SQLService(db)
        result = service.process_query(request.query)
        
        if result.get("error"):
            # Include SQL query in error response for debugging
            return error_response(
                message=result["error"],
                errors={
                    "sql_query": result.get("sql_query", "N/A"),
                    "intent": str(result.get("intent", "N/A"))
                },
                status_code=400
            )
        
        response_data = {
            "intent": result["intent"].intent.value,
            "confidence": round(result["intent"].confidence, 2),
            "sql_query": result["sql_query"],
            "result": result["result"],
            "execution_time_ms": round(result["execution_time_ms"], 2)
        }
        
        if request.explain:
            response_data["explanation"] = f"Query terdeteksi intent: {result['intent'].intent.value}. SQL yang dihasilkan melakukan query terhadap tabel: {', '.join(result['intent'].entity_types)}"
        
        return success_response(
            data=response_data,
            message="Query berhasil dieksekusi"
        )
        
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/intents", response_model=dict)
def list_intents():
    """
    List semua tipe intent yang tersedia.
    
    Response:
    ```json
    {
      "success": true,
      "data": {
        "intents": [
          {
            "type": "list",
            "description": "Ambil data santri, pesantren, dll",
            "examples": ["Tunjukkan semua santri", "Lihat list pesantren"]
          },
          ...
        ]
      }
    }
    ```
    """
    intents_info = [
        {
            "type": IntentType.LIST.value,
            "description": "Ambil data santri, pesantren, atau data lainnya",
            "examples": [
                "Tunjukkan semua santri",
                "Lihat list pesantren di Jawa Barat",
                "Tampilkan data santri pribadi"
            ]
        },
        {
            "type": IntentType.FILTER.value,
            "description": "Filter data berdasarkan kondisi tertentu",
            "examples": [
                "Santri dari Bandung yang miskin",
                "Pesantren di Jawa Barat dengan kategori sangat layak",
                "Orangtua yang pendapatannya kurang dari 2 juta"
            ]
        },
        {
            "type": IntentType.COUNT.value,
            "description": "Hitung jumlah total data",
            "examples": [
                "Berapa jumlah santri?",
                "Ada berapa pesantren di Tasikmalaya?",
                "Total santri miskin berapa?"
            ]
        },
        {
            "type": IntentType.STATISTICS.value,
            "description": "Statistik, agregasi, rata-rata",
            "examples": [
                "Rata-rata skor santri berapa?",
                "Distribusi kemiskinan santri",
                "Analisis kategori pesantren"
            ]
        },
        {
            "type": IntentType.RANKING.value,
            "description": "Ranking atau sorting data",
            "examples": [
                "Pesantren terbaik",
                "Top 10 santri dengan skor tertinggi",
                "Pesantren terburuk di kategori kelayakan"
            ]
        },
        {
            "type": IntentType.LOCATION.value,
            "description": "Query berbasis lokasi/peta",
            "examples": [
                "Peta distribusi santri",
                "Dimana lokasi pesantren di Bandung?",
                "Koordinat santri di Jawa Barat"
            ]
        },
        {
            "type": IntentType.DISTANCE.value,
            "description": "Query radius/jarak",
            "examples": [
                "Santri dalam radius 10 km dari pusat kota",
                "Pesantren terdekat dari lokasi ini",
                "Santri yang tinggal dekat pesantren"
            ]
        },
        {
            "type": IntentType.SCORING.value,
            "description": "Query tentang score/nilai",
            "examples": [
                "Berapa skor santri Ahmad?",
                "Kelayakan pesantren berapa?",
                "Penilaian kategori santri miskin"
            ]
        },
    ]
    
    return success_response(
        data={"intents": intents_info},
        message=f"Total {len(intents_info)} intent types tersedia"
    )


@router.post("/test", response_model=dict)
def test_nl2sql(db: Session = Depends(get_db)):
    """
    Test AI Query dengan query contoh.
    
    Berguna untuk testing tanpa perlu provide query sendiri.
    """
    test_queries = [
        "Tunjukkan 10 santri terbaru",
        "Berapa jumlah santri di Jawa Barat?",
        "Pesantren mana yang terbaik?",
        "Santri miskin dengan skor tertinggi siapa?",
    ]
    
    try:
        service = NL2SQLService(db)
        results = []
        
        for query in test_queries:
            result = service.process_query(query)
            intent_obj = result.get("intent")
            results.append({
                "query": query,
                "intent": intent_obj.intent.value if intent_obj else None,
                "success": result.get("error") is None,
                "error": result.get("error")
            })
        
        return success_response(
            data={"test_results": results},
            message="Test queries dijalankan"
        )
        
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.post("/query-map", response_model=dict)
def nl2sql_query_map(request: NL2SQLRequest, db: Session = Depends(get_db)):
    """
    Execute AI Query dan return GeoJSON untuk map visualization.
    
    Query example:
    - "Tampilkan lokasi semua santri miskin"
    - "Heatmap santri berdasarkan skor"
    - "Santri dalam radius 10km dari pusat Bandung"
    """
    import time
    start_time = time.time()
    
    try:
        service = NL2SQLService(db)
        result = service.process_query(request.query)
        execution_time = (time.time() - start_time) * 1000
        
        if result.get("error"):
            return error_response(
                message=result["error"],
                status_code=400
            )
        
        # Get result data
        data = result.get("result", [])
        intent_obj = result.get("intent")
        intent_type = intent_obj.intent.value if intent_obj else "unknown"
        
        # Generate GeoJSON if data exists
        geojson = None
        is_valid = False
        if data:
            from app.nl2sql.output_normalizer import OutputNormalizer
            geojson = OutputNormalizer.format_for_response(data, intent_type)
            
            # Validate GeoJSON (only if it's a dict/FeatureCollection)
            if isinstance(geojson, dict):
                is_valid = OutputNormalizer.validate_geojson_structure(geojson)
                
                # Add metadata
                geojson = OutputNormalizer.add_metadata_to_geojson(
                    geojson,
                    intent=intent_type,
                    query=request.query,
                    count=len(data)
                )
        
        return success_response(
            data={
                "intent": intent_type,
                "confidence": result.get("confidence", 0),
                "sql_query": result.get("sql_query", ""),
                "row_count": len(data) if isinstance(data, list) else 1,
                "geojson": geojson,
                "execution_time_ms": round(execution_time, 2),
                "valid_geojson": is_valid if geojson else False
            },
            message="GeoJSON query berhasil dijalankan"
        )
        
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/map/schema")
def get_map_schema():
    """Get GeoJSON schema dan integration guide untuk frontend."""
    return success_response(
        data={
            "geojson_format": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": ["longitude", "latitude"]
                        },
                        "properties": {
                            "id": "unique identifier",
                            "name": "feature name"
                        },
                        "id": "optional feature id"
                    }
                ],
                "properties": {
                    "count": "total features",
                    "generated_at": "ISO timestamp",
                    "intent": "query intent type",
                    "query": "original user query"
                },
                "bbox": ["minLon", "minLat", "maxLon", "maxLat"]
            },
            "intent_types": {
                "location": "Show features on map",
                "heatmap": "Show intensity-based heatmap",
                "distance": "Show features within radius",
                "list": "Return data as list (no map)"
            },
            "frontend_examples": {
                "leaflet": "https://leafletjs.com/examples/geojson/",
                "mapbox": "https://docs.mapbox.com/mapbox-gl-js/example/geojson-line/"
            },
            "coordinate_system": "WGS84 (EPSG:4326)",
            "bbox_format": "[minLongitude, minLatitude, maxLongitude, maxLatitude]"
        },
        message="GeoJSON schema untuk map integration"
    )

