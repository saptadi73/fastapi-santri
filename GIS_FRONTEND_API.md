# GIS Frontend API Endpoints

Backend endpoints optimized for frontend map visualization and heatmap rendering.

## Quick Test

```bash
# Santri Points
curl http://127.0.0.1:8000/gis/santri-points

# Pesantren Points  
curl http://127.0.0.1:8000/gis/pesantren-points

# Santri Heatmap
curl http://127.0.0.1:8000/gis/heatmap

# Pesantren Heatmap
curl http://127.0.0.1:8000/gis/pesantren-heatmap
```

---

## Endpoints

### 1. GET /gis/santri-points

Get santri locations as simple points for map rendering.

**Parameters:**
- `kategori` (optional): Filter by poverty category (Sangat Miskin, Miskin, Rentan, Tidak Miskin)
- `pesantren_id` (optional): Filter by pesantren
- `limit` (default: 1000, max: 5000)

**Response (Valid GeoJSON):**
```json
{
  "success": true,
  "message": "Retrieved 1 santri locations",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [106.994906, -6.160694]
        },
        "properties": {
          "id": "3e1b022b-b949-4e5a-a266-8b25d0924497",
          "name": "Aji Pangestu",
          "category": "Tidak Miskin",
          "score": 5,
          "pesantren_id": "bfc0e58b-de57-4f22-84e3-5c36cd2002de"
        }
      }
    ],
    "total": 1
  }
}
```

**Frontend Usage (Leaflet):**
```javascript
async function loadSantriPoints() {
  const res = await fetch('/gis/santri-points?limit=500');
  const data = await res.json();
  
  // GeoJSON FeatureCollection - fully compatible with Leaflet
  L.geoJSON(data.data, {
    pointToLayer: (feature, latlng) => {
      const categoryColors = {
        'Sangat Miskin': '#d32f2f',
        'Miskin': '#f57c00',
        'Rentan': '#fbc02d',
        'Tidak Miskin': '#388e3c'
      };
      
      const color = categoryColors[feature.properties.category] || '#999';
      
      return L.circleMarker(latlng, {
        radius: 8,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 2,
        color: '#fff'
      });
    },
    onEachFeature: (feature, layer) => {
      const props = feature.properties;
      layer.bindPopup(`
        <b>${props.name}</b><br>
        Score: ${props.score}<br>
        Category: ${props.category}
      `);
    }
  }).addTo(map);
}
```

---

### 2. GET /gis/pesantren-points

Get pesantren locations as simple points for map rendering.

**Parameters:**
- `kategori` (optional): Filter by quality category (sangat_layak, layak, cukup_layak, tidak_layak)
- `provinsi` (optional): Filter by province
- `limit` (default: 1000, max: 5000)

**Response (Valid GeoJSON):**
```json
{
  "success": true,
  "message": "Retrieved 1 pesantren locations",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [106.926292, -6.265486]
        },
        "properties": {
          "id": "b83d80cc-c35f-450a-b28c-895e4518e835",
          "name": "Mahasina",
          "nsp": "7625142018",
          "category": "sangat_layak",
          "score": 94,
          "province": "Jawa Barat",
          "regency": "Bekasi",
          "students": 700
        }
      }
    ],
    "total": 1
  }
}
```

**Frontend Usage (Leaflet):**
```javascript
async function loadPesantrenPoints() {
  const res = await fetch('/gis/pesantren-points?limit=500');
  const data = await res.json();
  
  // GeoJSON FeatureCollection - fully compatible with Leaflet
  L.geoJSON(data.data, {
    pointToLayer: (feature, latlng) => {
      const categoryIcons = {
        'sangat_layak': '🟢',
        'layak': '🟡',
        'cukup_layak': '🟠',
        'tidak_layak': '🔴'
      };
      
      const icon = categoryIcons[feature.properties.category] || '⚪';
      
      return L.marker(latlng, {
        icon: L.divIcon({
          className: 'marker-' + feature.properties.category,
          html: `<div class="marker-icon" title="${icon}">${icon}</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 32]
        })
      });
    },
    onEachFeature: (feature, layer) => {
      const props = feature.properties;
      layer.bindPopup(`
        <b>${props.name}</b><br>
        NSP: ${props.nsp}<br>
        Score: ${props.score}<br>
        Students: ${props.students}<br>
        Category: ${props.category}
      `);
    }
  }).addTo(map);
}
```

---

### 3. GET /gis/heatmap

Get santri heatmap data for density visualization.

**Parameters:**
- `kategori` (optional): Filter by poverty category

**Response (Valid GeoJSON with heatmap properties):**
```json
{
  "success": true,
  "message": "Generated heatmap with 1 santri points",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [106.994906, -6.160694]
        },
        "properties": {
          "intensity": 0.0125,
          "value": 5,
          "category": "Tidak Miskin"
        }
      }
    ],
    "total": 1,
    "intensity_min": 0,
    "intensity_max": 1.0
  }
}
```

**Frontend Usage (Leaflet.heat):**
```javascript
async function loadSantriHeatmap() {
  const res = await fetch('/gis/heatmap');
  const data = await res.json();
  
  // Convert GeoJSON features to [lat, lon, intensity] for Leaflet.heat
  const heatData = data.data.features.map(feature => [
    feature.geometry.coordinates[1],  // latitude
    feature.geometry.coordinates[0],  // longitude
    feature.properties.intensity      // intensity weight
  ]);
  
  L.heatLayer(heatData, {
    radius: 25,
    blur: 15,
    maxZoom: 17,
    gradient: {
      0.0: '#38006b',
      0.25: '#0064ff',
      0.5: '#00b4ff',
      0.75: '#ffff00',
      1.0: '#ff0000'
    }
  }).addTo(map);
}
```

---

### 4. GET /gis/pesantren-heatmap

Get pesantren heatmap data for quality/density visualization.

**Parameters:**
- `kategori` (optional): Filter by quality category

**Response (Valid GeoJSON with heatmap properties):**
```json
{
  "success": true,
  "message": "Generated heatmap with 1 pesantren points",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [106.926292, -6.265486]
        },
        "properties": {
          "intensity": 0.94,
          "value": 94,
          "category": "sangat_layak",
          "name": "Mahasina",
          "province": "Jawa Barat"
        }
      }
    ],
    "total": 1,
    "intensity_min": 0,
    "intensity_max": 1.0
  }
}
```

**Frontend Usage (Leaflet.heat):**
```javascript
async function loadPesantrenHeatmap() {
  const res = await fetch('/gis/pesantren-heatmap');
  const data = await res.json();
  
  // Convert GeoJSON features to [lat, lon, intensity] for Leaflet.heat
  const heatData = data.data.features.map(feature => [
    feature.geometry.coordinates[1],  // latitude
    feature.geometry.coordinates[0],  // longitude
    feature.properties.intensity      // intensity weight
  ]);
  
  L.heatLayer(heatData, {
    radius: 30,
    blur: 20,
    maxZoom: 17,
    gradient: {
      0.0: '#ff0000',
      0.5: '#ffff00',
      1.0: '#00ff00'
    }
  }).addTo(map);
}
```

---

## Frontend Integration Example

### HTML Setup

```html
<!-- Leaflet Map -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Heatmap Layer -->
<script src="https://unpkg.com/leaflet-heat@0.2.0/dist/leaflet-heat.js"></script>

<div id="map" style="height: 100vh;"></div>
```

### JavaScript Initialization

```javascript
// Initialize map
const map = L.map('map').setView([-7.5, 108.2], 9);

// Base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

// Layer control
const layers = {
  'Santri Points': null,
  'Santri Heatmap': null,
  'Pesantren Points': null,
  'Pesantren Heatmap': null
};

// Load data
async function initializeMaps() {
  // Santri Points
  const santriRes = await fetch('/gis/santri-points?limit=500');
  const santriData = await santriRes.json();
  layers['Santri Points'] = L.layerGroup();
  
  santriData.data.points.forEach(point => {
    L.circleMarker([point.lat, point.lon], {
      radius: 6,
      fillColor: getCategoryColor(point.category),
      fillOpacity: 0.8,
      weight: 1,
      color: '#fff'
    }).bindPopup(`<b>${point.name}</b><br>Score: ${point.score}`)
      .addTo(layers['Santri Points']);
  });
  
  // Pesantren Points
  const pesRes = await fetch('/gis/pesantren-points?limit=500');
  const pesData = pesRes.json();
  layers['Pesantren Points'] = L.layerGroup();
  
  pesData.data.points.forEach(point => {
    L.marker([point.lat, point.lon], {
      icon: L.icon({
        iconUrl: `/static/icons/${point.category}.png`,
        iconSize: [32, 32]
      })
    }).bindPopup(`<b>${point.name}</b><br>Score: ${point.score}`)
      .addTo(layers['Pesantren Points']);
  });
  
  // Layer control
  L.control.layers({}, layers).addTo(map);
}

function getCategoryColor(category) {
  const colors = {
    'Sangat Miskin': '#d32f2f',
    'Miskin': '#f57c00',
    'Rentan': '#fbc02d',
    'Tidak Miskin': '#388e3c',
    'sangat_layak': '#1b5e20',
    'layak': '#4caf50',
    'cukup_layak': '#fbc02d',
    'tidak_layak': '#d32f2f'
  };
  return colors[category] || '#999';
}

initializeMaps();
```

---

## Color Schemes

### Santri Map
- **Sangat Miskin**: #d32f2f (Red)
- **Miskin**: #f57c00 (Orange)
- **Rentan**: #fbc02d (Yellow)
- **Tidak Miskin**: #388e3c (Green)

### Pesantren Map
- **Sangat Layak**: #1b5e20 (Dark Green)
- **Layak**: #4caf50 (Light Green)
- **Cukup Layak**: #fbc02d (Yellow)
- **Tidak Layak**: #d32f2f (Red)

---

## Status

✅ **All endpoints tested and working**
- /gis/santri-points: ✅
- /gis/pesantren-points: ✅
- /gis/heatmap: ✅
- /gis/pesantren-heatmap: ✅
