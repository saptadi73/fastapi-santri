# NL2SQL Map Integration Guide

Panduan lengkap untuk mengintegrasikan GeoJSON output dari NL2SQL dengan aplikasi map (Leaflet/Mapbox).

## Table of Contents
1. [Overview](#overview)
2. [Auto Coordinate Support](#auto-coordinate-support)
3. [GeoJSON Format](#geojson-format)
4. [API Endpoints](#api-endpoints)
5. [Intent Types & Map Output](#intent-types--map-output)
6. [Frontend Integration Examples](#frontend-integration-examples)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Overview

NL2SQL Map Integration memungkinkan:
- **Spatial Queries**: Query data berdasarkan lokasi geografis
- **Heatmap Visualization**: Visualisasi intensitas/skor sebagai heatmap
- **Distance Queries**: Query feature dalam radius tertentu
- **GeoJSON Export**: Standar RFC 7946 compliant output

### Key Features
✓ RFC 7946 GeoJSON compliant  
✓ Automatic coordinate validation  
✓ Heatmap intensity normalization (0-1)  
✓ Bounding box calculation  
✓ JSON serialization safe  
✓ Leaflet & Mapbox compatible  

---

## Auto Coordinate Support

**NEW (Jan 2026)**: Koordinat otomatis ditambahkan ke semua query santri dan pesantren!

### Santri Queries

Setiap query santri (non-agregasi) otomatis menyertakan `latitude` dan `longitude`:

```
Query: "Berikan 10 santri dengan skor tertinggi"

Generated SQL:
SELECT sp.id, sp.nama, sp.latitude, sp.longitude, ss.skor_total
FROM santri_pribadi sp
JOIN santri_skor ss ON sp.id = ss.santri_id
ORDER BY ss.skor_total DESC
LIMIT 10

Response:
{
  "result": [
    {
      "id": "uuid-1",
      "nama": "Ahmad Hidayat",
      "latitude": -6.2088,
      "longitude": 106.8456,
      "skor_total": 92
    }
  ]
}
```

### Pesantren Queries

Setiap query pesantren (non-agregasi) otomatis JOIN dengan `pesantren_map` dan extract koordinat:

```
Query: "Pesantren dengan skor tertinggi di Jawa Barat"

Generated SQL:
SELECT pp.id, pp.nama, ps.skor_total, 
       ST_Y(pm.lokasi::geometry) as latitude,
       ST_X(pm.lokasi::geometry) as longitude
FROM pondok_pesantren pp
JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
JOIN pesantren_map pm ON pp.id = pm.pesantren_id
WHERE pp.provinsi = 'Jawa Barat'
ORDER BY ps.skor_total DESC
LIMIT 50

Response:
{
  "result": [
    {
      "id": "uuid-1",
      "nama": "Pondok Pesantren Al-Muhtadin",
      "latitude": -7.0562,
      "longitude": 107.7564,
      "skor_total": 95
    }
  ]
}
```

### Key Points

✅ **Automatic Inclusion**: Koordinat selalu ditambahkan otomatis  
✅ **No Extra Endpoint Needed**: Gunakan `/nl2sql/query` biasa  
✅ **Visualizable Immediately**: Data siap untuk peta interaktif  
✅ **Smart Exclusion**: Agregasi queries (GROUP BY) tidak include koordinat  

⚠️ **Aggregate Queries**: 
```
Query: "Berapa jumlah pesantren per kabupaten di Jawa Barat"

Result (tanpa latitude/longitude):
[
  { "kabupaten": "Bandung", "jumlah_pesantren": 45 },
  { "kabupaten": "Bogor", "jumlah_pesantren": 32 }
]
```

---

## GeoJSON Format

### Struktur Dasar

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "santri-1",
      "geometry": {
        "type": "Point",
        "coordinates": [107.6062, -6.9271]
      },
      "properties": {
        "nama_santri": "Ahmad Hidayat",
        "kategori_kemiskinan": "Miskin",
        "tahun_angkatan": 2023
      }
    }
  ],
  "properties": {
    "count": 3,
    "generated_at": "2026-01-01T11:25:06.825092",
    "intent": "location",
    "query": "Tampilkan lokasi semua santri"
  },
  "bbox": [107.5992, -6.9452, 107.6102, -6.8852]
}
```

### Koordinat Format
- **Format**: `[longitude, latitude]` (GeoJSON standard)
- **Sistem Koordinat**: WGS84 (EPSG:4326)
- **Validasi**: Otomatis check None/invalid values

### Properties
Setiap feature dapat memiliki properties custom:
```json
{
  "id": "santri-1",
  "nama_santri": "Ahmad",
  "kategori_kemiskinan": "Miskin",
  "skor": 75,
  "distance": 2.5,
  "intensity": 0.75
}
```

---

## API Endpoints

### 1. Intent Detection Only
```http
POST /nl2sql/detect-intent
Content-Type: application/json

{
  "query": "Tampilkan lokasi semua santri miskin"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "location",
    "confidence": 95,
    "keywords": ["lokasi", "tampilkan"],
    "entity_types": ["location"]
  }
}
```

### 2. Full NL2SQL Query
```http
POST /nl2sql/query
Content-Type: application/json

{
  "query": "Tampilkan lokasi semua santri miskin",
  "explain": false
}
```

**Response (Non-Spatial):**
```json
{
  "success": true,
  "data": {
    "intent": "filter",
    "confidence": 92,
    "sql_query": "SELECT * FROM santri_pribadi WHERE kategori_kemiskinan='Miskin'",
    "result": [
      {"id": 1, "nama_santri": "Ahmad", ...}
    ],
    "execution_time_ms": 45.23
  }
}
```

### 3. **NEW** - Map Query (GeoJSON Output)
```http
POST /nl2sql/query-map
Content-Type: application/json

{
  "query": "Tampilkan lokasi semua santri miskin"
}
```

**Response (Spatial - GeoJSON):**
```json
{
  "success": true,
  "data": {
    "intent": "location",
    "confidence": 95,
    "sql_query": "SELECT * FROM santri_pribadi WHERE ...",
    "row_count": 24,
    "geojson": {
      "type": "FeatureCollection",
      "features": [...],
      "properties": {...},
      "bbox": [...]
    },
    "execution_time_ms": 52.10,
    "valid_geojson": true
  }
}
```

### 4. Map Schema & Documentation
```http
GET /nl2sql/map/schema
```

**Response:**
```json
{
  "success": true,
  "data": {
    "geojson_format": {...},
    "intent_types": {
      "location": "Show features on map",
      "heatmap": "Show intensity-based heatmap",
      "distance": "Show features within radius"
    },
    "coordinate_system": "WGS84 (EPSG:4326)",
    "bbox_format": "[minLon, minLat, maxLon, maxLat]"
  }
}
```

---

## Intent Types & Map Output

### 1. LOCATION Intent
**Tujuan**: Tampilkan lokasi features pada map  
**Query Example**: "Tampilkan lokasi semua santri"

**Output**:
- Standard GeoJSON FeatureCollection
- Properties: All data fields except lat/lon
- Geometry: Point dengan [longitude, latitude]

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "id": "santri-1",
      "geometry": {"type": "Point", "coordinates": [107.6062, -6.9271]},
      "properties": {"nama_santri": "Ahmad", "skor": 75}
    }
  ],
  "bbox": [...]
}
```

### 2. HEATMAP Intent
**Tujuan**: Visualisasi intensitas/skor sebagai heatmap  
**Query Example**: "Heatmap santri berdasarkan skor"

**Output**:
- GeoJSON dengan intensity field (0-1 normalized)
- Property: `heatmap: true`
- Intensity calculation: `(value - min) / (max - min)`

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "geometry": {"type": "Point", "coordinates": [107.6062, -6.9271]},
      "properties": {
        "nama_santri": "Ahmad",
        "skor": 75,
        "intensity": 0.75
      }
    }
  ],
  "properties": {
    "heatmap": true,
    "intensity_range": [50, 100]
  }
}
```

**Heatmap Usage (Leaflet.heat)**:
```javascript
// Extract coordinates and intensity
const heatData = geojson.features.map(f => [
  f.geometry.coordinates[1],  // lat
  f.geometry.coordinates[0],  // lon
  f.properties.intensity      // value (0-1)
]);

// Create heatmap layer
L.heatLayer(heatData, {
  radius: 25,
  blur: 15,
  maxZoom: 17,
  minOpacity: 0.2,
  gradient: {0.4: 'blue', 0.65: 'lime', 1: 'red'}
}).addTo(map);
```

### 3. DISTANCE Intent
**Tujuan**: Query features dalam radius tertentu  
**Query Example**: "Santri dalam radius 10km dari pusat Bandung"

**Output**:
- GeoJSON dengan center point feature
- Distance field dalam km
- Sorted by distance (ascending)
- Properties: center coordinates dan radius

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "type": "center",
        "latitude": -6.9100,
        "longitude": 107.6050,
        "radius_km": 10
      }
    },
    {
      "geometry": {"coordinates": [107.6062, -6.9271]},
      "properties": {
        "nama_santri": "Ahmad",
        "distance": 2.5
      }
    }
  ]
}
```

**Usage (Circle visualization)**:
```javascript
// Add center point
const center = geojson.properties.center;
L.circleMarker([center.latitude, center.longitude], {
  radius: 5,
  fillColor: '#ff7800',
  color: '#000',
  weight: 2,
  opacity: 1,
  fillOpacity: 0.8
}).addTo(map);

// Add radius circle
const radiusKm = geojson.properties.radius_km || 10;
L.circle([center.latitude, center.longitude], {
  radius: radiusKm * 1000,  // Convert to meters
  color: 'red',
  fill: false,
  weight: 2,
  opacity: 0.5,
  dashArray: '5, 5'
}).addTo(map);
```

### 4. Other Intents (LIST, FILTER, COUNT)
**Output**: Regular JSON (non-GeoJSON)
- LOCATION required untuk GeoJSON
- Heatmap memerlukan intensity field
- Distance memerlukan distance field

---

## Frontend Integration Examples

### Leaflet.js Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Query Map</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-heat/0.2.0/leaflet-heat.min.js"></script>
  <style>
    #map { height: 600px; }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    // Initialize map
    const map = L.map('map').setView([-6.9271, 107.6062], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'OpenStreetMap'
    }).addTo(map);

    // Fetch GeoJSON from AI Query
    const query = "Heatmap santri berdasarkan skor";
    fetch('/nl2sql/query-map', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query})
    })
    .then(r => r.json())
    .then(response => {
      const geojson = response.data.geojson;
      
      // Add GeoJSON to map
      L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
          const intensity = feature.properties.intensity || 0.5;
          const color = intensity > 0.7 ? '#ff0000' : intensity > 0.4 ? '#ffff00' : '#00ff00';
          
          return L.circleMarker(latlng, {
            radius: 8,
            fillColor: color,
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
          }).bindPopup(`<b>${feature.properties.nama_santri}</b><br>Skor: ${feature.properties.skor}`);
        }
      }).addTo(map);
      
      // Auto-fit bounds
      if (geojson.bbox) {
        const bounds = [[geojson.bbox[1], geojson.bbox[0]], 
                        [geojson.bbox[3], geojson.bbox[2]]];
        map.fitBounds(bounds);
      }
    });
  </script>
</body>
</html>
```

### Mapbox GL JS Example

```html
<!DOCTYPE html>
<html>
<head>
  <script src='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js'></script>
  <link href='https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css' rel='stylesheet' />
  <style>
    #map { height: 600px; }
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
    mapboxgl.accessToken = 'YOUR_TOKEN';
    const map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [107.6062, -6.9271],
      zoom: 12
    });

    // Fetch GeoJSON
    const query = "Tampilkan lokasi santri miskin";
    fetch('/nl2sql/query-map', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query})
    })
    .then(r => r.json())
    .then(response => {
      const geojson = response.data.geojson;
      
      map.on('load', () => {
        // Add source
        map.addSource('features', {type: 'geojson', data: geojson});
        
        // Add layer
        map.addLayer({
          id: 'features',
          type: 'circle',
          source: 'features',
          paint: {
            'circle-radius': 8,
            'circle-color': '#007cbf',
            'circle-opacity': 0.8,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#fff'
          }
        });
        
        // Add popup
        map.on('click', 'features', (e) => {
          const feature = e.features[0];
          new mapboxgl.Popup()
            .setLngLat(feature.geometry.coordinates)
            .setHTML(`<b>${feature.properties.nama_santri}</b>`)
            .addTo(map);
        });
      });
    });
  </script>
</body>
</html>
```

---

## Advanced Usage

### 1. Distance Query dengan Custom Center

```javascript
const query = "Santri dalam radius 5km dari koordinat -6.9100, 107.6050";
// Backend akan auto-parse latitude dan longitude dari query
```

### 2. Multi-Layer Map dengan Heatmap + Location

```javascript
// Fetch heatmap
fetch('/nl2sql/query-map', {
  method: 'POST',
  body: JSON.stringify({query: "Heatmap santri"})
})
.then(r => r.json())
.then(response => {
  const heatmapGeoJSON = response.data.geojson;
  
  // Add heatmap layer
  const heatData = heatmapGeoJSON.features.map(f => [
    f.geometry.coordinates[1],
    f.geometry.coordinates[0],
    f.properties.intensity
  ]);
  
  L.heatLayer(heatData, {radius: 25, blur: 15}).addTo(map);
  
  // Also add markers
  L.geoJSON(heatmapGeoJSON).addTo(map);
});
```

### 3. Custom Styling per Intent

```javascript
// Styling function
function styleFeature(feature) {
  if (feature.properties.intensity) {
    // Heatmap style
    return {
      color: feature.properties.intensity > 0.7 ? '#ff0000' : '#00ff00'
    };
  } else if (feature.properties.distance) {
    // Distance style - color by proximity
    return {
      color: feature.properties.distance < 5 ? '#ff0000' : '#ff9900'
    };
  } else {
    // Default location style
    return {color: '#0066cc'};
  }
}

L.geoJSON(geojson, {
  style: styleFeature,
  pointToLayer: (feature, latlng) => {
    const style = styleFeature(feature);
    return L.circleMarker(latlng, {radius: 8, ...style});
  }
}).addTo(map);
```

### 4. Auto-Zoom & Fit Bounds

```javascript
// Use bbox dari response
if (response.data.geojson.bbox) {
  const [minLon, minLat, maxLon, maxLat] = response.data.geojson.bbox;
  const bounds = [[minLat, minLon], [maxLat, maxLon]];
  
  // Leaflet
  map.fitBounds(bounds, {padding: 50});
  
  // Mapbox
  map.fitBounds(bounds, {padding: 50});
}
```

---

## Error Handling & Validation

### 1. Check Valid GeoJSON

```python
from app.nl2sql.output_normalizer import OutputNormalizer

# Validate after generation
is_valid = OutputNormalizer.validate_geojson_structure(geojson)
if not is_valid:
    # Handle invalid GeoJSON
    print("Invalid GeoJSON structure")
```

### 2. Handle Missing Coordinates

```javascript
// Frontend: Filter out invalid features
const validFeatures = geojson.features.filter(f => {
  const coords = f.geometry.coordinates;
  return coords && coords.length === 2 && 
         !isNaN(coords[0]) && !isNaN(coords[1]);
});
```

### 3. Error Response Handling

```javascript
fetch('/nl2sql/query-map', {
  method: 'POST',
  body: JSON.stringify({query})
})
.then(r => r.json())
.then(response => {
  if (!response.success) {
    console.error('Error:', response.message);
    // Show error to user
  } else if (!response.data.valid_geojson) {
    console.warn('GeoJSON validation failed');
  } else {
    // Process valid GeoJSON
  }
})
.catch(error => console.error('Network error:', error));
```

---

## Coordinate Support Details

### Santri Coordinate Extraction

Koordinat santri diambil langsung dari tabel `santri_pribadi`:

```sql
-- Santri pribadi memiliki kolom latitude dan longitude
SELECT sp.id, sp.nama, sp.latitude, sp.longitude
FROM santri_pribadi sp
WHERE sp.kategori_kemiskinan = 'Miskin'
```

### Pesantren Coordinate Extraction

Koordinat pesantren diambil dari PostGIS geometry field di tabel `pesantren_map`:

```sql
-- PostGIS geometry functions untuk extract koordinat
SELECT pp.id, pp.nama,
       ST_Y(pm.lokasi::geometry) as latitude,  -- Y = latitude
       ST_X(pm.lokasi::geometry) as longitude  -- X = longitude
FROM pondok_pesantren pp
JOIN pesantren_map pm ON pp.id = pm.pesantren_id
```

### System Prompt Specification

OpenAI GPT-4 diberikan instruksi eksplisit untuk menambahkan koordinat:

```
INSTRUKSI SPESIAL:
- Jika query memiliki entity "pesantren" dan BUKAN agregasi: 
  WAJIB JOIN dengan pesantren_map dan extract koordinat dengan 
  ST_Y(pm.lokasi::geometry) as latitude, 
  ST_X(pm.lokasi::geometry) as longitude
  
- Jika query memiliki entity "santri" dan BUKAN agregasi: 
  WAJIB SELECT latitude, longitude dari santri_pribadi
```

Instruksi ini ditambahkan ke setiap request ke OpenAI untuk memastikan koordinat selalu disertakan.

---

## Troubleshooting

### Issue 1: Features tidak muncul di map
**Penyebab**: Koordinat invalid atau format salah
**Solusi**:
```python
# Check dalam database
SELECT id, nama_santri, latitude, longitude 
FROM santri_pribadi 
WHERE latitude IS NULL OR longitude IS NULL;
```

### Issue 2: GeoJSON tidak serialize
**Penyebab**: Data type tidak JSON compatible (Decimal, datetime, UUID)
**Solusi**: OutputNormalizer otomatis handle ini
```python
result = OutputNormalizer.format_for_response(rows, intent)
# Semua types sudah dinormalisasi
```

### Issue 3: Heatmap tidak terlihat
**Penyebab**: Intensity field tidak ditemukan atau range terlalu sempit
**Solusi**:
```python
# Check data memiliki skor field
SELECT nama_santri, skor FROM santri_pribadi LIMIT 5;

# Verify range
SELECT MIN(skor), MAX(skor) FROM santri_pribadi;
```

### Issue 4: Distance queries lambat
**Penyebab**: Missing spatial index pada koordinat
**Solusi**: Buat spatial index
```sql
CREATE INDEX idx_santri_location 
ON santri_pribadi USING GIST(ll_to_earth(latitude, longitude));
```

---

## Performance Tips

1. **Limit hasil**: Gunakan LIMIT dalam query
   ```
   "Tampilkan 100 santri terdekat"
   ```

2. **Use clustering** untuk large datasets:
   ```javascript
   L.markerClusterGroup().addTo(map);
   ```

3. **Cache GeoJSON**:
   ```javascript
   const cache = new Map();
   const key = query;
   if (cache.has(key)) {
     return cache.get(key);
   }
   ```

4. **Lazy load** layers:
   ```javascript
   map.on('moveend', () => {
     // Reload GeoJSON for current viewport
   });
   ```

---

## Resources

- [GeoJSON RFC 7946](https://tools.ietf.org/html/rfc7946)
- [Leaflet Documentation](https://leafletjs.com/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

**Version**: 1.0  
**Last Updated**: 2026-01-01  
**Status**: Production Ready ✓
