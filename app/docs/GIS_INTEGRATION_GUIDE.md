<!-- markdownlint-disable MD033 MD034 -->

# Panduan Integrasi GIS - Santri & Pesantren Map

## Ringkasan Sistem

Aplikasi FastAPI ini menyediakan **DUA sistem pemetaan GIS yang terpisah**:

### Santri Map - Pemetaan Lokasi Santri

- **Tabel**: `santri_map`
- **Tujuan**: Memetakan lokasi santri berdasarkan tingkat kemiskinan
- **Auto-update**: Saat scoring santri dihitung/dihitung ulang
- **Endpoint**: `/santri-map/*`

### Pesantren Map - Pemetaan Lokasi Pesantren

- **Tabel**: `pesantren_map`
- **Tujuan**: Memetakan lokasi pesantren berdasarkan kelayakan fasilitas
- **Auto-update**: Saat scoring pesantren dihitung/dihitung ulang
- **Endpoint**: `/pesantren-map/*`

---

## Status Implementasi

| Komponen | Santri Map | Pesantren Map | Status |
|----------|-----------|---------------|--------|
| Tabel Database | ✅ | ✅ | Dibuat |
| Model SQLAlchemy | ✅ | ✅ | Lengkap |
| Service Layer | ✅ | ✅ | Lengkap |
| API Endpoints | ✅ | ✅ | Aktif |
| Auto-update | ✅ | ✅ | Berfungsi |
| GeoJSON Support | ✅ | ✅ | Berfungsi |
| Spatial Queries | ✅ | ✅ | Berfungsi |
| Data Test | ✅ | ✅ | Tersedia |

---

## API Endpoints

### Santri Map API

#### Get GeoJSON (untuk peta)

```bash
GET /santri-map/geojson?kategori=Miskin&pesantren_id={uuid}&limit=1000
```

**Parameters:**

- `kategori` (optional): Sangat Miskin, Miskin, Rentan, Tidak Miskin
- `pesantren_id` (optional): Filter by pesantren UUID
- `limit` (default: 1000, max: 5000)

**Response:** GeoJSON FeatureCollection dengan geometry POINT

#### Get by Bounding Box (viewport optimization)

```bash
GET /santri-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2
```

**Use case:** Load only visible santri when user pans/zooms map

#### Get Statistics

```bash
GET /santri-map/statistics
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_santri": 1,
    "with_location": 1,
    "without_location": 0,
    "by_category": {
      "Tidak Miskin": 1
    }
  }
}
```

### Pesantren Map API

#### Get GeoJSON

```bash
GET /pesantren-map/geojson?kategori=layak&provinsi=Jawa%20Barat&kabupaten=Tasikmalaya&limit=1000
```

**Parameters:**

- `kategori` (optional): sangat_layak, layak, cukup_layak, tidak_layak
- `provinsi` (optional): Filter by province name
- `kabupaten` (optional): Filter by regency name
- `limit` (default: 1000, max: 5000)

#### Get by Bounding Box

```bash
GET /pesantren-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2
```

#### Get Statistics

```bash
GET /pesantren-map/statistics
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_pesantren": 1,
    "with_location": 1,
    "without_location": 0,
    "by_category": {
      "sangat_layak": 1
    }
  }
}
```

---

## Frontend Integration

### Opsi 1: Leaflet (Open Source)

**Install:**

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

**Example Code:**

```javascript
// Initialize map
const map = L.map('map').setView([-7.5, 108.2], 9);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Load Santri GeoJSON
fetch('http://127.0.0.1:8000/santri-map/geojson?limit=500')
  .then(res => res.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: getColorByCategory(feature.properties.kategori_kemiskinan),
          fillOpacity: 0.8
        });
      },
      onEachFeature: (feature, layer) => {
        layer.bindPopup(`
          <b>${feature.properties.nama}</b><br>
          Skor: ${feature.properties.skor_terakhir}<br>
          Kategori: ${feature.properties.kategori_kemiskinan}
        `);
      }
    }).addTo(map);
  });
```

### Opsi 2: Mapbox GL JS (Advanced)

**Install:**

```html
<link href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css" rel="stylesheet">
<script src="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js"></script>
```

**Example Code:**

```javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [108.2, -7.5],
  zoom: 9
});

map.on('load', () => {
  // Add Santri layer
  map.addSource('santri', {
    type: 'geojson',
    data: 'http://127.0.0.1:8000/santri-map/geojson?limit=500'
  });

  map.addLayer({
    id: 'santri-points',
    type: 'circle',
    source: 'santri',
    paint: {
      'circle-radius': 8,
      'circle-color': [
        'match',
        ['get', 'kategori_kemiskinan'],
        'Sangat Miskin', '#d32f2f',
        'Miskin', '#f57c00',
        'Rentan', '#fbc02d',
        'Tidak Miskin', '#388e3c',
        '#999'
      ]
    }
  });
});
```

### Opsi 3: React dengan react-leaflet

```jsx
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { useEffect, useState } from 'react';

function SantriMap() {
  const [geojson, setGeojson] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/santri-map/geojson')
      .then(res => res.json())
      .then(data => setGeojson(data));
  }, []);

  return (
    <MapContainer center={[-7.5, 108.2]} zoom={9} style={{height: '100vh'}}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {geojson && (
        <GeoJSON
          data={geojson}
          pointToLayer={(feature, latlng) => {
            return L.circleMarker(latlng, {
              radius: 8,
              fillColor: getColor(feature.properties.kategori_kemiskinan)
            });
          }}
        />
      )}
    </MapContainer>
  );
}
```

---

## Use Cases

### Santri Map - Analisis Kemiskinan Spasial

**Tujuan:**

- Identifikasi cluster santri miskin di wilayah tertentu
- Prioritas program bantuan berdasarkan lokasi
- Analisis sebaran kemiskinan per pesantren

**Contoh Implementasi:**

```javascript
// Filter santri "Sangat Miskin" di Jawa Barat
fetch('/santri-map/geojson?kategori=Sangat Miskin')
  .then(res => res.json())
  .then(geojson => {
    // Tampilkan di peta dengan marker merah
    displayOnMap(geojson, { color: 'red' });
  });
```

### Pesantren Map - Pemetaan Kelayakan Fasilitas

**Tujuan:**

- Identifikasi pesantren yang perlu perbaikan fasilitas
- Prioritas alokasi dana bantuan
- Analisis distribusi pesantren berkualitas

**Contoh Implementasi:**

```javascript
// Filter pesantren "tidak_layak" untuk prioritas bantuan
fetch('/pesantren-map/geojson?kategori=tidak_layak')
  .then(res => res.json())
  .then(geojson => {
    // Tampilkan di peta dengan icon warning
    displayOnMap(geojson, { icon: 'warning' });
  });
```

### Dual Map View - Analisis Korelasi

**Tujuan:**

- Lihat hubungan antara kualitas pesantren dan tingkat kemiskinan santri
- Analisis apakah pesantren berkualitas buruk → santri lebih miskin

**Contoh Implementasi:**

```javascript
// Load both layers
Promise.all([
  fetch('/santri-map/geojson').then(r => r.json()),
  fetch('/pesantren-map/geojson').then(r => r.json())
]).then(([santriData, pesantrenData]) => {
  // Display both on same map with different styles
  displaySantri(santriData);  // Circle markers
  displayPesantren(pesantrenData); // Pin markers
});
```

---

## Performance Optimization

### Use Bounding Box untuk Large Datasets

```javascript
map.on('moveend', () => {
  const bounds = map.getBounds();
  fetch(`/santri-map/bbox?min_lon=${bounds.getWest()}&...`)
    .then(res => res.json())
    .then(data => updateVisibleMarkers(data));
});
```

### Clustering untuk Banyak Data

```javascript
// Use MarkerCluster plugin
const markers = L.markerClusterGroup();
L.geoJSON(geojson, {
  pointToLayer: (feature, latlng) => {
    return L.marker(latlng);
  }
}).addTo(markers);
map.addLayer(markers);
```

### Separate Concerns

```javascript
// Pisahkan logika fetch dan display
async function fetchSantriData(filters) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/santri-map/geojson?${params}`);
  return response.json();
}

function displaySantriOnMap(geojson) {
  L.geoJSON(geojson, {...}).addTo(map);
}

// Usage
const data = await fetchSantriData({ kategori: 'Miskin' });
displaySantriOnMap(data);
```

---

## Troubleshooting

### Issue 1: Map tidak muncul

**Solution:**

Pastikan Leaflet CSS dimuat:

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

Set explicit height untuk container:

```html
<div id="map" style="height: 600px;"></div>
```

### Issue 2: CORS error

**Solution:**

Pastikan CORS sudah dikonfigurasi di FastAPI (sudah ada di `main.py`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Data tidak muncul

**Check:**

```bash
# Test API directly
curl http://127.0.0.1:8000/santri-map/statistics
curl http://127.0.0.1:8000/pesantren-map/statistics

# Harus return data > 0
```

---

## Resources

- [Leaflet Documentation](https://leafletjs.com/)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/)
- [GeoJSON Specification](https://geojson.org/)
- [PostGIS Documentation](https://postgis.net/docs/)

---

## Checklist Implementation

- [x] Create santri_map and pesantren_map tables
- [x] Implement auto-update on scoring
- [x] Create GeoJSON endpoints
- [x] Create bounding box endpoints
- [x] Create statistics endpoints
- [x] Test with sample data
- [x] Create demo HTML page
- [x] Document API endpoints
- [x] Add to API_DOCUMENTATION.md

**Status: FULLY IMPLEMENTED & TESTED**

---

Developed with ❤️ for FastAPI Santri Project
Date: December 31, 2025
