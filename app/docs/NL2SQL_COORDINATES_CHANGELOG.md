# NL2SQL Coordinates Feature - Changelog

**Date**: January 15, 2026  
**Status**: ✅ Completed and Tested

---

## Overview

Implemented automatic coordinate support for NL2SQL queries. Now all santri and pesantren queries automatically include latitude/longitude for map visualization.

---

## What's New

### 1. Santri Queries - Auto Latitude/Longitude

**Before:**
```sql
SELECT sp.id, sp.nama
FROM santri_pribadi sp
WHERE sp.kategori_kemiskinan = 'Miskin'
```

**After:**
```sql
SELECT sp.id, sp.nama, sp.latitude, sp.longitude
FROM santri_pribadi sp
WHERE sp.kategori_kemiskinan = 'Miskin'
```

### 2. Pesantren Queries - PostGIS Coordinate Extraction

**Before:**
```sql
SELECT pp.id, pp.nama
FROM pondok_pesantren pp
JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
```

**After:**
```sql
SELECT pp.id, pp.nama, ps.skor_total,
       ST_Y(pm.lokasi::geometry) as latitude,
       ST_X(pm.lokasi::geometry) as longitude
FROM pondok_pesantren pp
JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
JOIN pesantren_map pm ON pp.id = pm.pesantren_id
```

### 3. Smart Exclusion for Aggregates

Aggregate queries (with GROUP BY) correctly exclude coordinates:

```
Query: "Berapa jumlah pesantren per kabupaten"

Result:
[
  { "kabupaten": "Bandung", "jumlah_pesantren": 45 },
  { "kabupaten": "Bogor", "jumlah_pesantren": 32 }
]
```

No latitude/longitude added (correct behavior).

---

## Implementation Details

### Modified Files

1. **app/nl2sql/nl2sql_service.py**
   - Enhanced system prompt with explicit coordinate instructions
   - Added coordinate requirements to user prompt
   - Distinguishes between regular and aggregate queries

2. **app/nl2sql/schema_context.json**
   - Added rule: "PENTING untuk PETA: Query pesantren harus JOIN dengan pesantren_map"
   - Added rule: "PENTING untuk PETA: Query santri harus SELECT latitude dan longitude"
   - Added query examples showing coordinate extraction patterns
   - Updated query_examples with "pesantren_untuk_peta" showing ST_X()/ST_Y() usage

3. **app/docs/NL2SQL_DOCUMENTATION.md**
   - Added new section: "Map Integration (Coordinates)"
   - Documented coordinate support for santri and pesantren
   - Added examples with coordinates in responses
   - Documented PostGIS functions used

4. **app/docs/NL2SQL_MAP_INTEGRATION.md**
   - Added table of contents entry for "Auto Coordinate Support"
   - Documented automatic coordinate inclusion
   - Explained smart exclusion for aggregate queries
   - Added coordinate extraction methods details

### System Prompt Changes

Added to user prompt for every query:

```
INSTRUKSI SPESIAL:
- Jika query memiliki entity "pesantren" dan BUKAN agregasi: 
  WAJIB JOIN dengan pesantren_map dan extract koordinat dengan 
  ST_Y(pm.lokasi::geometry) as latitude, 
  ST_X(pm.lokasi::geometry) as longitude
  
- Jika query memiliki entity "santri" dan BUKAN agregasi: 
  WAJIB SELECT latitude, longitude dari santri_pribadi
```

This explicit instruction ensures OpenAI reliably includes coordinates.

---

## Test Results

### Santri Queries ✅

```
Query: "Berikan 10 santri dengan skor tertinggi"

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

### Pesantren Queries ✅

```
Query: "Pesantren dengan skor tertinggi di Jawa Barat"

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

### Aggregate Queries (Correct Exclusion) ✅

```
Query: "Berapa jumlah pesantren per kabupaten di Jawa Barat"

Response:
{
  "result": [
    { "kabupaten": "Bandung", "jumlah_pesantren": 45 },
    { "kabupaten": "Bogor", "jumlah_pesantren": 32 }
  ]
}
```

No coordinates included (as expected).

---

## Usage Examples

### Simple Detail Query with Coordinates

```bash
curl -X POST "http://localhost:8000/nl2sql/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Santri miskin di Bandung"
  }'
```

**Response includes:** latitude, longitude automatically

### Map Integration (Frontend)

```javascript
// Fetch query results with coordinates
const response = await fetch('/nl2sql/query', {
  method: 'POST',
  body: JSON.stringify({ query: "Pesantren di Jawa Barat" })
});

const data = await response.json();

// Create map markers directly
data.data.result.forEach(item => {
  L.marker([item.latitude, item.longitude])
    .setPopupContent(item.nama)
    .addTo(map);
});
```

---

## Technical Notes

### PostGIS Functions

- **ST_X()**: Extract X coordinate (longitude)
- **ST_Y()**: Extract Y coordinate (latitude)
- **Geometry Type**: Cast to geometry with `::geometry`

Example:
```sql
ST_Y(pm.lokasi::geometry) as latitude
ST_X(pm.lokasi::geometry) as longitude
```

### Coordinate System

- **Format**: [longitude, latitude] in GeoJSON
- **System**: WGS84 (EPSG:4326)
- **Range**: Longitude: -180 to 180, Latitude: -90 to 90

### Database Requirements

- **Santri**: Must have `latitude` and `longitude` columns in `santri_pribadi`
- **Pesantren**: Must have `lokasi` geometry column in `pesantren_map`

---

## Breaking Changes

None. This is a pure enhancement that adds fields to existing responses.

---

## Future Improvements

1. [ ] Support for custom coordinate columns
2. [ ] Coordinate validation/error handling
3. [ ] Coordinate transformation (other CRS support)
4. [ ] Clustering on map for large result sets
5. [ ] Heatmap intensity calculation based on scores

---

## Testing

Run test files to verify:

```bash
# Test santri queries with coordinates
python test_santri_coordinates_check.py

# Test pesantren queries with coordinates
python test_pesantren_koordinat_debug.py
```

---

## Questions?

- Check `app/docs/NL2SQL_DOCUMENTATION.md` for coordinate details
- Check `app/docs/NL2SQL_MAP_INTEGRATION.md` for map integration
- Check `app/nl2sql/schema_context.json` for query examples

