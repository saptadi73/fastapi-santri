#!/usr/bin/env python
"""Quick Reference - NL2SQL Map Integration API."""

print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                  NL2SQL MAP INTEGRATION - QUICK REFERENCE                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

📍 ENDPOINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  POST /nl2sql/detect-intent
    └─ Detect intent only (no SQL execution)
    └─ Response: intent, confidence, keywords, entity_types

  POST /nl2sql/query
    └─ Full NL2SQL pipeline (SQL + execution)
    └─ Response: sql_query, result (list/dict)

  POST /nl2sql/query-map ⭐ NEW
    └─ NL2SQL + GeoJSON output for map visualization
    └─ Response: geojson (FeatureCollection), valid_geojson, execution_time_ms

  GET /nl2sql/map/schema
    └─ Get GeoJSON schema and integration guide
    └─ Response: geojson_format, intent_types, examples


🎯 INTENT TYPES FOR MAPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  LOCATION
    Query: "Tampilkan lokasi semua santri"
    Output: GeoJSON FeatureCollection with Point geometry
    Map: Markers/circles at each location
    
  HEATMAP
    Query: "Heatmap santri berdasarkan skor"
    Output: GeoJSON with intensity field (0-1 normalized)
    Map: Color-intensity visualization, needs leaflet.heat plugin
    
  DISTANCE
    Query: "Santri dalam radius 10km dari pusat Bandung"
    Output: GeoJSON with center point + distance field, sorted by distance
    Map: Radius circle + markers, features sorted by proximity


📋 GEOJSON STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "id": "santri-1",
        "geometry": {
          "type": "Point",
          "coordinates": [LONGITUDE, LATITUDE]  ← [107.6062, -6.9271]
        },
        "properties": {
          "nama_santri": "Ahmad Hidayat",
          "kategori_kemiskinan": "Miskin",
          "skor": 75,
          "intensity": 0.75  ← For heatmap (0-1)
        }
      }
    ],
    "properties": {
      "count": 3,
      "intent": "location",
      "query": "user query",
      "heatmap": true  ← For heatmap intent
    },
    "bbox": [minLon, minLat, maxLon, maxLat]  ← [107.599, -6.945, 107.610, -6.885]
  }


🚀 QUICK START - API CALLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # LOCATION - Show santri locations
  curl -X POST http://localhost:8000/nl2sql/query-map \\
    -H "Content-Type: application/json" \\
    -d '{"query": "Tampilkan lokasi semua santri miskin"}'

  # HEATMAP - Show intensity by score
  curl -X POST http://localhost:8000/nl2sql/query-map \\
    -H "Content-Type: application/json" \\
    -d '{"query": "Heatmap santri berdasarkan skor"}'

  # DISTANCE - Show features in radius
  curl -X POST http://localhost:8000/nl2sql/query-map \\
    -H "Content-Type: application/json" \\
    -d '{"query": "Santri dalam radius 10km dari pusat Bandung"}'


🗺️ JAVASCRIPT IMPLEMENTATION (LEAFLET)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  // Initialize map
  const map = L.map('map').setView([-6.9271, 107.6062], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

  // Fetch and display GeoJSON
  fetch('/nl2sql/query-map', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'Tampilkan lokasi santri'})
  })
  .then(r => r.json())
  .then(response => {
    if (response.success) {
      const geojson = response.data.geojson;
      
      // Add to map
      L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
          return L.circleMarker(latlng, {
            radius: 8,
            fillColor: '#ff7800',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
          }).bindPopup(feature.properties.nama_santri);
        }
      }).addTo(map);
      
      // Auto-fit bounds
      if (geojson.bbox) {
        const bounds = [[geojson.bbox[1], geojson.bbox[0]], 
                        [geojson.bbox[3], geojson.bbox[2]]];
        map.fitBounds(bounds);
      }
    }
  });


🐍 PYTHON IMPLEMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  import requests
  import json

  # Make request to NL2SQL map endpoint
  response = requests.post(
    'http://localhost:8000/nl2sql/query-map',
    json={'query': 'Tampilkan lokasi semua santri miskin'}
  )
  
  data = response.json()
  
  if data['success']:
    geojson = data['data']['geojson']
    
    # Validate GeoJSON
    print(f"Valid: {data['data']['valid_geojson']}")
    print(f"Features: {len(geojson['features'])}")
    print(f"Bounds: {geojson.get('bbox')}")
    
    # Save to file
    with open('santri_locations.geojson', 'w') as f:
      json.dump(geojson, f, indent=2)


⚙️ CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Database fields required:
    ✓ latitude (float) - WGS84 latitude
    ✓ longitude (float) - WGS84 longitude
    ✓ For heatmap: intensity field (skor, nilai, weight, etc)
    ✓ For distance: distance field in kilometers

  Example santri_pribadi schema:
    id BIGINT PRIMARY KEY
    nama_santri VARCHAR
    latitude FLOAT
    longitude FLOAT
    skor INTEGER  ← For heatmap
    kategori_kemiskinan VARCHAR


✅ VALIDATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  □ Database has latitude/longitude fields
  □ Coordinates are WGS84 (EPSG:4326)
  □ No NULL coordinates in query results
  □ Heatmap has intensity field
  □ Distance query has center point
  □ GeoJSON validates RFC 7946
  □ Frontend can render GeoJSON
  □ Leaflet/Mapbox libraries loaded


📖 FULL DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  See: NL2SQL_MAP_INTEGRATION.md
  Sections:
    ▪ API Endpoints (detailed)
    ▪ GeoJSON Format Specification
    ▪ Frontend Examples (Leaflet, Mapbox)
    ▪ Heatmap Configuration
    ▪ Distance Radius Queries
    ▪ Error Handling & Validation
    ▪ Performance Optimization
    ▪ Troubleshooting Guide


🔗 RELATED FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Core Components:
    ✓ app/nl2sql/geojson_generator.py (8 methods)
    ✓ app/nl2sql/output_normalizer.py (updated with GeoJSON)
    ✓ app/routes/nl2sql_routes.py (new endpoints)

  Test Files:
    ✓ test_geojson_generator.py
    ✓ test_nl2sql_map.py
    ✓ test_nl2sql_system.py

  Documentation:
    ✓ NL2SQL_MAP_INTEGRATION.md
    ✓ NL2SQL_DOCUMENTATION.md
    ✓ NL2SQL_QUICK_START.md


💡 TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Use /nl2sql/query-map for spatial queries, /nl2sql/query for others
  2. Always check response['data']['valid_geojson'] before using
  3. Heatmap needs leaflet-heat plugin (not built-in to Leaflet)
  4. Use bbox for auto-fitting map view to data extent
  5. Cache GeoJSON responses if query doesn't change
  6. For large datasets, add LIMIT to query or use clustering
  7. Validate coordinates before upload: -90 to 90 lat, -180 to 180 lon


╔════════════════════════════════════════════════════════════════════════════════╗
║  Version: 1.0 | Status: Production Ready ✓ | Last Updated: 2026-01-01         ║
╚════════════════════════════════════════════════════════════════════════════════╝
""")
