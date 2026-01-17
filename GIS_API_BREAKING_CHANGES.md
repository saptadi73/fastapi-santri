# GIS API Response Format Changes

## ⚠️ BREAKING CHANGES - Frontend Update Required

Perubahan endpoint GIS telah mengubah struktur response untuk mendukung pagination dan optimasi performa. Frontend HARUS diupdate untuk menangani format baru.

---

## 📋 Perubahan per Endpoint

### 1. **`GET /gis/santri-points`** ❌ BREAKING CHANGE

#### SEBELUMNYA (Old Response Format):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [...] },
      "properties": { "id": "...", "nama": "...", ... }
    }
  ]
}
```

#### SEKARANG (New Response Format):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [...] },
      "properties": { "id": "...", "nama": "...", ... }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 1000,
    "total": 25000,
    "pages": 25
  }
}
```

#### Frontend Update Required:
```javascript
// OLD - Tidak bekerja lagi
const response = await fetch('/gis/santri-points?kategori=Sangat Miskin');
const geojson = response.json();
L.geoJSON(geojson).addTo(map);  // ❌ Error: features not found

// NEW - Harus diupdate
const response = await fetch('/gis/santri-points?kategori=Sangat Miskin&page=1&limit=1000');
const data = response.json();
const geojson = {
  type: data.type,
  features: data.features
};
L.geoJSON(geojson).addTo(map);  // ✅ Bekerja

// Atau akses pagination info
console.log(`Halaman ${data.pagination.page} dari ${data.pagination.pages}`);
```

#### Parameters Baru:
- `page` (opsional, default: 1) - Nomor halaman
- `limit` (opsional, default: 1000, max: 5000) - Item per halaman

---

### 2. **`GET /gis/pesantren-points`** ❌ BREAKING CHANGE

#### SEBELUMNYA:
```json
{
  "type": "FeatureCollection",
  "features": [...]
}
```

#### SEKARANG:
```json
{
  "type": "FeatureCollection",
  "features": [...],
  "pagination": {
    "page": 1,
    "limit": 1000,
    "total": 5000,
    "pages": 5
  }
}
```

#### Frontend Update:
```javascript
// OLD
const data = await fetch('/gis/pesantren-points').then(r => r.json());
L.geoJSON(data).addTo(map);

// NEW
const data = await fetch('/gis/pesantren-points?page=1&limit=1000').then(r => r.json());
L.geoJSON({ type: data.type, features: data.features }).addTo(map);
```

#### Parameters Baru:
- `page` (opsional, default: 1)
- `limit` (opsional, default: 1000, max: 5000)

---

### 3. **`GET /gis/pesantren-heatmap`** ❌ BREAKING CHANGE

#### SEBELUMNYA:
```json
[
  { "lat": -6.2, "lng": 106.8, "weight": 75, "kategori": "Sangat Layak", "skor": 85 },
  { "lat": -6.3, "lng": 106.9, "weight": 65, "kategori": "Layak", "skor": 75 }
]
```

#### SEKARANG:
```json
{
  "data": [
    { "lat": -6.2, "lng": 106.8, "weight": 75, "kategori": "Sangat Layak", "skor": 85, "id": "..." },
    { "lat": -6.3, "lng": 106.9, "weight": 65, "kategori": "Layak", "skor": 75, "id": "..." }
  ],
  "pagination": {
    "page": 1,
    "limit": 5000,
    "total": 15000,
    "pages": 3
  }
}
```

#### Frontend Update:
```javascript
// OLD
const heatmapData = await fetch('/gis/pesantren-heatmap').then(r => r.json());
const heatLayer = L.heatLayer(heatmapData.map(p => [p.lat, p.lng, p.weight]));

// NEW
const response = await fetch('/gis/pesantren-heatmap?page=1&limit=5000').then(r => r.json());
const heatmapData = response.data; // ⚠️ Akses property 'data'
const heatLayer = L.heatLayer(heatmapData.map(p => [p.lat, p.lng, p.weight]));
```

#### Parameters Baru:
- `page` (opsional, default: 1)
- `limit` (opsional, default: 5000, max: 10000)

---

### 4. **`GET /gis/heatmap`** ❌ BREAKING CHANGE

#### SEBELUMNYA:
```json
[
  { "lat": -6.2, "lng": 106.8, "weight": 50, "ekonomi": "Sangat Miskin", "skor": 45 },
  { "lat": -6.3, "lng": 106.9, "weight": 60, "ekonomi": "Miskin", "skor": 55 }
]
```

#### SEKARANG:
```json
{
  "data": [
    { "lat": -6.2, "lng": 106.8, "weight": 50, "ekonomi": "Sangat Miskin", "skor": 45, "id": "..." },
    { "lat": -6.3, "lng": 106.9, "weight": 60, "ekonomi": "Miskin", "skor": 55, "id": "..." }
  ],
  "pagination": {
    "page": 1,
    "limit": 5000,
    "total": 50000,
    "pages": 10
  }
}
```

#### Frontend Update:
```javascript
// OLD
const heatmapData = await fetch('/gis/heatmap?kategori=Sangat Miskin').then(r => r.json());
const heatLayer = L.heatLayer(heatmapData.map(p => [p.lat, p.lng, p.weight]));

// NEW
const response = await fetch('/gis/heatmap?kategori=Sangat Miskin&page=1&limit=5000').then(r => r.json());
const heatmapData = response.data; // ⚠️ Akses property 'data'
const heatLayer = L.heatLayer(heatmapData.map(p => [p.lat, p.lng, p.weight]));
```

#### Parameters Baru:
- `page` (opsional, default: 1)
- `limit` (opsional, default: 5000, max: 10000)

---

### 5. **`GET /gis/choropleth/santri-kabupaten`** ✅ NO CHANGE
- Response format tetap sama (masih JSONB GeoJSON FeatureCollection)
- No breaking changes

### 6. **`GET /gis/choropleth/pesantren-kabupaten`** ✅ NO CHANGE
- Response format tetap sama
- No breaking changes

### 7. **`GET /gis/choropleth/stats`** ✅ NO CHANGE
- Response format tetap sama
- No breaking changes

---

## 🔧 Frontend Implementation Guide

### Opsi 1: Update Client-side (Recommended untuk quick fix)

```javascript
class GISClient {
  async getSantriPoints(kategori, page = 1, limit = 1000) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(kategori && { kategori })
    });
    
    const response = await fetch(`/gis/santri-points?${params}`);
    return response.json();
  }
  
  async getPesantrenPoints(provinsi, page = 1, limit = 1000) {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(provinsi && { provinsi })
    });
    
    const response = await fetch(`/gis/pesantren-points?${params}`);
    return response.json();
  }
  
  async getHeatmapData(type = 'santri', page = 1, limit = 5000) {
    const url = type === 'pesantren' 
      ? `/gis/pesantren-heatmap?page=${page}&limit=${limit}`
      : `/gis/heatmap?page=${page}&limit=${limit}`;
    
    const response = await fetch(url);
    const data = await response.json();
    return data.data; // Return hanya array, bukan wrapper object
  }
  
  async getChoroplethData(type = 'santri', provinsi = null) {
    const endpoint = type === 'pesantren'
      ? '/gis/choropleth/pesantren-kabupaten'
      : '/gis/choropleth/santri-kabupaten';
    
    const params = provinsi ? `?provinsi=${provinsi}` : '';
    const response = await fetch(`${endpoint}${params}`);
    return response.json(); // Format unchanged
  }
}

// Usage di Component
const gisClient = new GISClient();

// Fetch santri points dengan pagination
const santriData = await gisClient.getSantriPoints('Sangat Miskin', 1, 1000);
L.geoJSON({
  type: santriData.type,
  features: santriData.features
}).addTo(map);

// Fetch heatmap (otomatis extract 'data' property)
const heatmapData = await gisClient.getHeatmapData('santri', 1, 5000);
L.heatLayer(heatmapData.map(p => [p.lat, p.lng, p.weight])).addTo(map);

// Track pagination
console.log(`Page ${santriData.pagination.page}/${santriData.pagination.pages}`);
```

### Opsi 2: Backend Adapter (Jika ada Legacy Code)

Untuk backward compatibility, bisa tambah endpoint baru yang return format lama:

```python
@router.get("/santri-points/legacy")
def santri_points_legacy(
    kategori: str | None = None,
    pesantren_id: str | None = None,
    db: Session = Depends(get_db),
):
    """Legacy endpoint - returns old format without pagination"""
    data = santri_points(kategori=kategori, pesantren_id=pesantren_id, db=db)
    # Return hanya features (format lama)
    return {
        "type": data["type"],
        "features": data["features"]
    }
```

---

## 📊 Migration Checklist

- [ ] Update GIS layer initialization code untuk handle pagination
- [ ] Update heatmap layer code untuk akses `data` property
- [ ] Add pagination controls (prev/next buttons) jika diperlukan
- [ ] Test semua endpoint dengan berbagai parameter
- [ ] Update documentation/swagger
- [ ] Update unit tests
- [ ] Monitor API responses di console browser
- [ ] Test dengan data besar (>10k items)

---

## ⚡ Performance Tips

1. **Gunakan limit optimal:**
   - Heatmap: 5000-10000 items per page
   - Points: 1000-2000 items per page (untuk detail properties)

2. **Implement infinite scroll:**
   ```javascript
   let currentPage = 1;
   const loadMorePesantren = async () => {
     const data = await gisClient.getPesantrenPoints(provinsi, currentPage++, 1000);
     if (data.features.length === 0) {
       console.log('No more data');
       return;
     }
     // Add to existing layer
     L.geoJSON(data).addTo(map);
   };
   ```

3. **Cache responses:**
   ```javascript
   const cache = new Map();
   const getCachedData = async (key, fetcher) => {
     if (cache.has(key)) return cache.get(key);
     const data = await fetcher();
     cache.set(key, data);
     return data;
   };
   ```

4. **Lazy load:** Load data hanya saat user scroll/pan ke area tersebut

---

## 🐛 Troubleshooting

### Error: "Cannot read property 'features' of undefined"
```javascript
// ❌ Wrong
const features = response.features;

// ✅ Correct
const features = response.json().then(data => data.features);
```

### Error: "Cannot iterate over undefined"
```javascript
// ❌ Wrong - response langsung adalah array
heatmapData.map(p => [p.lat, p.lng, p.weight])

// ✅ Correct
const response = await fetch(...);
const data = response.json();
data.data.map(p => [p.lat, p.lng, p.weight]) // Access 'data' property
```

### Error: Infinite scroll tidak berhenti
```javascript
// ✅ Check pagination
if (data.pagination.page >= data.pagination.pages) {
  console.log('Reached last page');
  return; // Stop loading
}
```

---

## 📞 API Reference Quick Links

- Endpoints dengan pagination:
  - `/gis/santri-points` (new)
  - `/gis/pesantren-points` (new)
  - `/gis/pesantren-heatmap` (new)
  - `/gis/heatmap` (new)

- Endpoints unchanged:
  - `/gis/choropleth/santri-kabupaten`
  - `/gis/choropleth/pesantren-kabupaten`
  - `/gis/choropleth/stats`

---

**Updated:** January 17, 2026  
**Status:** Breaking Changes - Requires Frontend Update
