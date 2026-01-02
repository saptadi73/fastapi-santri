<!-- markdownlint-disable MD022 MD023 MD031 MD032 MD040 MD007 MD060 MD036 MD009 MD005 -->

# API Documentation - FastAPI Santri

**Base URL:** `http://localhost:8000`

---

### Create Asset
Create a single asset with optional photos (multipart/form-data).

```
POST /api/santri-asset
Content-Type: multipart/form-data
```

**Form Fields:**
```

```text
POST /api/{entity}/{entity_id}/photos
```

**Update Photo:**

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "jenis_aset": "motor",
    "jumlah": 1,
    "nilai_perkiraan": 15000000,
    "foto_asset": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440099",
        "asset_id": "770e8400-e29b-41d4-a716-446655440002",
        "nama_file": "motor_1.jpg",
        "url_photo": "/uploads/asset/770e8400-e29b-41d4-a716-446655440002/motor_1.jpg"
      }
    ]
  }
}
```

Notes:
- Valid `jenis_aset`: `motor`, `mobil`, `sepeda`, `hp`, `laptop`, `lahan`, `ternak`, `alat_kerja`, `lainnya`.
- If your UI uses "handphone", map it to `hp` to avoid validation errors.
- Photos uploaded here are appended; use the photo update endpoint to replace specific photos.

```text
PUT /api/{entity}/photos/{foto_id}
```

**Delete Photo:**

```text
DELETE /api/{entity}/photos/{foto_id}
```

Where `{entity}` is one of: `santri-pribadi`, `santri-orangtua`, `santri-asset`, `santri-rumah`

### File Upload Requirements

- **Supported Formats:** jpg, jpeg, png, webp
- **Max Size per File:** 5MB
- **Multiple Files:** Yes, allowed in add/create operations

### Photo Response Format

All photo endpoints return consistent structure:

```json
{
  "id": "UUID",
  "santri_id": "UUID" | "orangtua_id" | "asset_id" | "rumah_id",
  "nama_file": "filename.jpg",
  "url_photo": "/uploads/entity/filename.jpg"
}
```

### Photo Objects (Standardized)

- Fields: `id`, `nama_file`, `url_photo`, plus parent reference (`santri_id` | `orangtua_id` | `asset_id` | `rumah_id` | `pesantren_id` as applicable).
- `url_photo` always uses forward slashes (`/`) and is a relative path to be prefixed by your API base (e.g., `${API_BASE_URL}/uploads/...`).

### Static Uploads

- All uploaded files are served under `/uploads`.
- Example: `url_photo: /uploads/santri/{santri_id}/filename.jpg`.
- Clients should prefix with the API base URL, e.g. `${API_BASE_URL}/uploads/...`.
- All paths are URL-style (`/`), regardless of the server OS.

**Note:** When updating or deleting, old file is automatically unlinked from disk.

---

## Authentication

### Login
Authenticate and get access token.

```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## GIS / Map Endpoints

### Get Santri Points (GeoJSON)
Retrieve santri locations with optional filtering by administrative area.

```
GET /gis/santri-points?provinsi=Jawa Barat&kabupaten=Bandung&kecamatan=Bandung Kota
```

**Query Parameters:**
- `provinsi` (optional): Filter by province name
- `kabupaten` (optional): Filter by district name
- `kecamatan` (optional): Filter by sub-district name

**Response (200 OK):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [107.61, -6.92]
      },
      "properties": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nama": "Ahmad Hidayat",
        "provinsi": "Jawa Barat",
        "kabupaten": "Bandung",
        "kecamatan": "Bandung Kota"
      }
    }
  ]
}
```

### Get Heatmap Data
Retrieve santri location coordinates for heatmap visualization.

```
GET /gis/heatmap
```

**Response (200 OK):**
```json
[
  {
    "lat": -6.92,
    "lng": 107.61,
    "weight": 1
  },
  {
    "lat": -6.93,
    "lng": 107.62,
    "weight": 1
  }
]
```

### Choropleth Map - Santri by Kabupaten
Get aggregated santri statistics per kabupaten for choropleth visualization.

```
GET /gis/choropleth/santri-kabupaten?provinsi=Jawa Barat&kategori_kemiskinan=Miskin
```

**Query Parameters:**
- `provinsi` (optional): Filter by province name
- `kategori_kemiskinan` (optional): Filter by poverty category (Sangat Miskin, Miskin, Rentan, Tidak Miskin)

**Response (200 OK):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[107.5, -6.8], [107.7, -6.8], [107.7, -7.0], [107.5, -7.0], [107.5, -6.8]]]
      },
      "properties": {
        "kabupaten": "Bandung",
        "provinsi": "Jawa Barat",
        "total_santri": 1250,
        "sangat_miskin": 320,
        "miskin": 450,
        "rentan": 380,
        "tidak_miskin": 100,
        "avg_skor": 65.5,
        "pct_sangat_miskin": 25.6,
        "pct_miskin": 36.0
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[108.2, -7.3], [108.5, -7.3], [108.5, -7.6], [108.2, -7.6], [108.2, -7.3]]]
      },
      "properties": {
        "kabupaten": "Tasikmalaya",
        "provinsi": "Jawa Barat",
        "total_santri": 890,
        "sangat_miskin": 280,
        "miskin": 340,
        "rentan": 210,
        "tidak_miskin": 60,
        "avg_skor": 68.2,
        "pct_sangat_miskin": 31.5,
        "pct_miskin": 38.2
      }
    }
  ]
}
```

**Properties Explanation:**
- `total_santri`: Total number of santri in the kabupaten
- `sangat_miskin`: Count of "Sangat Miskin" category
- `miskin`: Count of "Miskin" category
- `rentan`: Count of "Rentan" category
- `tidak_miskin`: Count of "Tidak Miskin" category
- `avg_skor`: Average poverty score (0-100)
- `pct_sangat_miskin`: Percentage of santri in "Sangat Miskin" category
- `pct_miskin`: Percentage of santri in "Miskin" category

**Use Case - Leaflet/Mapbox Visualization:**
```javascript
// Fetch choropleth data
const response = await fetch('/gis/choropleth/santri-kabupaten');
const geojson = await response.json();

// Add to Leaflet map with color scale
L.geoJSON(geojson, {
  style: function(feature) {
    return {
      fillColor: getColor(feature.properties.avg_skor),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  },
  onEachFeature: function(feature, layer) {
    const props = feature.properties;
    layer.bindPopup(`
      <b>${props.kabupaten}</b><br>
      Total Santri: ${props.total_santri}<br>
      Sangat Miskin: ${props.sangat_miskin} (${props.pct_sangat_miskin}%)<br>
      Miskin: ${props.miskin} (${props.pct_miskin}%)<br>
      Avg Score: ${props.avg_skor}
    `);
  }
}).addTo(map);

// Color scale based on average score
function getColor(score) {
  return score > 80 ? '#d73027' :  // Sangat Miskin (dark red)
         score > 65 ? '#fc8d59' :  // Miskin (orange)
         score > 45 ? '#fee08b' :  // Rentan (yellow)
                      '#91cf60';   // Tidak Miskin (green)
}
```

### Choropleth Map - Pesantren by Kabupaten
Get aggregated pesantren statistics per kabupaten for choropleth visualization.

```
GET /gis/choropleth/pesantren-kabupaten?provinsi=Jawa Barat&kategori_kelayakan=Layak
```

**Query Parameters:**
- `provinsi` (optional): Filter by province name
- `kategori_kelayakan` (optional): Filter by eligibility category (Sangat Layak, Layak, Cukup Layak, Kurang Layak)

**Response (200 OK):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[107.5, -6.8], [107.7, -6.8], [107.7, -7.0], [107.5, -7.0], [107.5, -6.8]]]
      },
      "properties": {
        "kabupaten": "Bandung",
        "provinsi": "Jawa Barat",
        "total_pesantren": 45,
        "sangat_layak": 12,
        "layak": 18,
        "cukup_layak": 10,
        "kurang_layak": 5,
        "avg_skor": 72.5,
        "total_santri_pesantren": 5600,
        "pct_sangat_layak": 26.7,
        "pct_layak": 40.0
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[108.2, -7.3], [108.5, -7.3], [108.5, -7.6], [108.2, -7.6], [108.2, -7.3]]]
      },
      "properties": {
        "kabupaten": "Tasikmalaya",
        "provinsi": "Jawa Barat",
        "total_pesantren": 38,
        "sangat_layak": 8,
        "layak": 15,
        "cukup_layak": 12,
        "kurang_layak": 3,
        "avg_skor": 68.8,
        "total_santri_pesantren": 4200,
        "pct_sangat_layak": 21.1,
        "pct_layak": 39.5
      }
    }
  ]
}
```

**Properties Explanation:**
- `total_pesantren`: Total number of pesantren in the kabupaten
- `sangat_layak`: Count of "Sangat Layak" category
- `layak`: Count of "Layak" category
- `cukup_layak`: Count of "Cukup Layak" category
- `kurang_layak`: Count of "Kurang Layak" category
- `avg_skor`: Average eligibility score (0-100)
- `total_santri_pesantren`: Total santri across all pesantren in kabupaten
- `pct_sangat_layak`: Percentage of "Sangat Layak" pesantren
- `pct_layak`: Percentage of "Layak" pesantren

### Choropleth Statistics
Get summary statistics for choropleth visualization options.

```
GET /gis/choropleth/stats
```

**Response (200 OK):**
```json
{
  "santri_categories": [
    { "kategori": "Miskin", "count": 1250 },
    { "kategori": "Rentan", "count": 890 },
    { "kategori": "Sangat Miskin", "count": 650 },
    { "kategori": "Tidak Miskin", "count": 210 }
  ],
  "pesantren_categories": [
    { "kategori": "Layak", "count": 85 },
    { "kategori": "Sangat Layak", "count": 45 },
    { "kategori": "Cukup Layak", "count": 38 },
    { "kategori": "Kurang Layak", "count": 12 }
  ],
  "kabupaten_list": [
    "Bandung",
    "Bogor",
    "Cirebon",
    "Garut",
    "Tasikmalaya"
  ],
  "provinsi_list": [
    "Banten",
    "Jawa Barat",
    "Jawa Tengah",
    "Jawa Timur"
  ]
}
```

**Use Case:**
- Populate filter dropdowns in UI
- Display available categories for legend
- Show data distribution statistics

---

## Santri Pribadi (Core Data)

### List All Santri
Retrieve all santri with pagination and filters.

```
GET /api/santri-pribadi?page=1&per_page=20&search=Ahmad&provinsi=Jawa Barat&kabupaten=Bandung&jenis_kelamin=L
```

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `search` (optional): Search by name or NIK
- `provinsi` (optional): Filter by province
- `kabupaten` (optional): Filter by district
- `jenis_kelamin` (optional): Filter by gender (L/P)
- `pesantren_id` (optional): Filter by pesantren UUID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data santri berhasil diambil",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nama": "Ahmad Hidayat",
      "nik": "3271091234567890",
      "jenis_kelamin": "L",
      "provinsi": "Jawa Barat",
      "kabupaten": "Bandung",
      "pesantren_id": "660e8400-e29b-41d4-a716-446655440099",
      "pesantren_nama": "Pondok Pesantren Al-Ikhlas",
      "foto_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Get Santri Detail
Retrieve full details of a santri including all related data.

```
GET /api/santri-pribadi/{santri_id}
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Detail santri berhasil diambil",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nama": "Ahmad Hidayat",
    "nik": "3271091234567890",
    "no_kk": "3271091234567800",
    "tempat_lahir": "Bandung",
    "tanggal_lahir": "2008-05-15",
    "jenis_kelamin": "L",
    "status_tinggal": "mondok",
    "lama_mondok_tahun": 2,
    "pesantren_id": "660e8400-e29b-41d4-a716-446655440099",
    "pesantren": {
      "id": "660e8400-e29b-41d4-a716-446655440099",
      "nama": "Pondok Pesantren Al-Ikhlas"
    },
    "provinsi": "Jawa Barat",
    "kabupaten": "Bandung",
    "kecamatan": "Bandung Kota",
    "desa": "Desa Maju",
    "latitude": -6.92,
    "longitude": 107.61,
    "foto_santri": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "nama_file": "ahmad_1.jpg",
        "url_photo": "/uploads/santri/ahmad_1.jpg"
      }
    ]
  }
}
```

### Create New Santri
Create a new santri with optional photos (multipart/form-data).

```
POST /api/santri-pribadi
Content-Type: multipart/form-data
```

**Form Fields:**
```
nama: "Ahmad Hidayat" (required)
jenis_kelamin: "L" (required)
pesantren_id: "660e8400-e29b-41d4-a716-446655440099" (optional - UUID pesantren)
nik: "3271091234567890"
no_kk: "3271091234567800"
tempat_lahir: "Bandung"
tanggal_lahir: "2008-05-15" (YYYY-MM-DD)
status_tinggal: "mondok"
lama_mondok_tahun: 2
provinsi: "Jawa Barat"
kabupaten: "Bandung"
kecamatan: "Bandung Kota"
desa: "Desa Maju"
latitude: -6.92 (optional)
longitude: 107.61 (optional)
foto_files: [file1.jpg, file2.jpg] (optional, max 5MB each)
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Santri berhasil ditambahkan",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nama": "Ahmad Hidayat",
    "foto_count": 2
  }
}
```

### Update Santri
Update santri data (partial update).

```
PUT /api/santri-pribadi/{santri_id}
Content-Type: multipart/form-data
```

**Form Fields:** (all optional)
```
nama: "Ahmad Hidayat Baru"
pesantren_id: "660e8400-e29b-41d4-a716-446655440099" (change pesantren)
provinsi: "Jawa Timur"
kabupaten: "Surabaya"
...
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Santri berhasil diupdate",
  "data": { ... }
}
```

### Delete Santri
Delete santri and all associated photos.

```
DELETE /api/santri-pribadi/{santri_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Santri dan foto berhasil dihapus",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Alias Paths (without `/api`)
All Santri Pribadi endpoints are also available without the `/api` prefix using `/santri-pribadi`. The request and response formats are identical.

Examples:
```
GET    /santri-pribadi
GET    /santri-pribadi/{santri_id}
POST   /santri-pribadi
PUT    /santri-pribadi/{santri_id}
DELETE /santri-pribadi/{santri_id}
POST   /santri-pribadi/{santri_id}/photos
DELETE /santri-pribadi/photos/{foto_id}
```

### Add Photos to Santri
Add multiple photos to an existing santri.

```
POST /api/santri-pribadi/{santri_id}/photos
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto_files: [file1.jpg, file2.jpg, ...]
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "2 foto berhasil ditambahkan",
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "nama_file": "ahmad_1.jpg",
      "url_photo": "/uploads/santri/ahmad_1.jpg"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "nama_file": "ahmad_2.jpg",
      "url_photo": "/uploads/santri/ahmad_2.jpg"
    }
  ]
}
```

### Update Photo
Replace a santri photo with a new one.

```
PUT /api/santri-pribadi/photos/{foto_id}
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto: file.jpg
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Foto berhasil diupdate",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "nama_file": "ahmad_new.jpg",
    "url_photo": "/uploads/santri/ahmad_new.jpg"
  }
}
```

### Delete Photo
Delete a single santri photo.

```
DELETE /api/santri-pribadi/photos/{foto_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Foto berhasil dihapus",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

---

## Santri Orangtua (Parents)

### List All Orangtua for a Santri
Retrieve all parents/guardians for a specific santri.

```
GET /api/santri-orangtua?santri_id={uuid}&page=1&per_page=20&hubungan=ayah
```

**Query Parameters:**
- `santri_id` (optional, UUID): Filter by santri ID
- `pesantren_id` (optional, UUID): Filter by pesantren ID
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `search` (optional): Search by nama or NIK
- `hubungan` (optional): Filter by relationship (ayah/ibu/wali)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data orangtua berhasil diambil",
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nama": "Budi Santoso",
      "hubungan": "ayah",
      "pekerjaan": "Petani",
      "status_hidup": "hidup",
      "foto_count": 1,
      "foto_orangtua": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440003",
          "nama_file": "budi_1.jpg",
          "url_photo": "/uploads/orangtua/660e8400-e29b-41d4-a716-446655440001/budi_1.jpg"
        }
      ]
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "nama": "Nur Azizah",
      "hubungan": "ibu",
      "pekerjaan": "Ibu Rumah Tangga",
      "status_hidup": "hidup",
      "foto_count": 1,
      "foto_orangtua": [
        {
          "id": "880e8400-e29b-41d4-a716-446655440004",
          "nama_file": "nur_1.jpg",
          "url_photo": "/uploads/orangtua/660e8400-e29b-41d4-a716-446655440002/nur_1.jpg"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 2,
    "total_pages": 1
  }
}
```

### Get Orangtua Detail
Retrieve full details of a parent/guardian including photos.

```
GET /api/santri-orangtua/{orangtua_id}
```

**Path Parameters:**
- `orangtua_id` (UUID): Orangtua ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "nama": "Budi Santoso",
    "nik": "3271081234567890",
    "hubungan": "ayah",
    "pendidikan": "SMP",
    "pekerjaan": "Petani",
    "pendapatan_bulanan": 2500000,
    "status_hidup": "hidup",
    "kontak_telepon": "081234567890",
    "foto_orangtua": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440003",
        "orangtua_id": "660e8400-e29b-41d4-a716-446655440001",
        "nama_file": "budi_1.jpg",
        "url_photo": "/uploads/orangtua/budi_1.jpg"
      }
    ]
  }
}
```

### Create New Orangtua
Create a new parent/guardian with optional photos.

```
POST /api/santri-orangtua
Content-Type: multipart/form-data
```

**Form Fields:**
```
santri_id: "550e8400-e29b-41d4-a716-446655440000"
nama: "Budi Santoso"
hubungan: "ayah"
nik: "3271081234567890"
pendidikan: "SMP"
pekerjaan: "Petani"
pendapatan_bulanan: 2500000
status_hidup: "hidup"
kontak_telepon: "081234567890"
fotos: [file1.jpg, file2.jpg] (optional, max 5MB each)
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "nama": "Budi Santoso",
    "nik": "3271081234567890",
    "hubungan": "ayah",
    "pendidikan": "SMP",
    "pekerjaan": "Petani",
    "pendapatan_bulanan": 2500000,
    "status_hidup": "hidup",
    "kontak_telepon": "081234567890",
    "foto_orangtua": []
  }
}
```

### Update Orangtua
Update parent/guardian data (partial update).

```
PUT /api/santri-orangtua/{orangtua_id}
Content-Type: multipart/form-data
```

**Form Fields:** (all optional)
```
nama: "Budi Santoso"
nik: "3271081234567890"
hubungan: "ayah"
pendidikan: "SMA"
pekerjaan: "Petani"
pendapatan_bulanan: 3000000
status_hidup: "hidup"
kontak_telepon: "081234567890"
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

### Delete Orangtua
Delete a parent/guardian and all associated photos.

```
DELETE /api/santri-orangtua/{orangtua_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

### Add Photos to Orangtua
Add multiple photos to an existing orangtua.

```
POST /api/santri-orangtua/{orangtua_id}/photos
Content-Type: multipart/form-data
```

**Form Fields:**
```
fotos: [file1.jpg, file2.jpg, ...]
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "2 foto berhasil ditambahkan",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "orangtua_id": "660e8400-e29b-41d4-a716-446655440001",
      "nama_file": "budi_1.jpg",
      "url_photo": "/uploads/orangtua/budi_1.jpg"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440004",
      "orangtua_id": "660e8400-e29b-41d4-a716-446655440001",
      "nama_file": "budi_2.jpg",
      "url_photo": "/uploads/orangtua/budi_2.jpg"
    }
  ]
}
```

### Update Orangtua Photo
Replace an orangtua photo with a new one.

```
PUT /api/santri-orangtua/photos/{foto_id}
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto: file.jpg
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Foto berhasil diupdate",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "orangtua_id": "660e8400-e29b-41d4-a716-446655440001",
    "nama_file": "budi_new.jpg",
    "url_photo": "/uploads/orangtua/budi_new.jpg"
  }
}
```

### Delete Orangtua Photo
Delete a single orangtua photo.

```
DELETE /api/santri-orangtua/photos/{foto_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Foto berhasil dihapus",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440003"
  }
}
```

---

## Santri Rumah (House)

### List All Rumah
Retrieve all house records with pagination and filters.

```
GET /api/santri-rumah?page=1&per_page=20&santri_id={uuid}
```

**Query Parameters:**
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page
- `santri_id` (optional): Filter by santri ID
- `pesantren_id` (optional, UUID): Filter by pesantren ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data rumah berhasil diambil",
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "status_rumah": "milik_sendiri",
      "jenis_lantai": "keramik",
      "jenis_dinding": "tembok",
      "jenis_atap": "genteng",
      "akses_air_bersih": "layak",
      "daya_listrik_va": "2200",
      "foto_rumah": [
        {
          "id": "990e8400-e29b-41d4-a716-446655440005",
          "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
          "nama_file": "rumah_1.jpg",
          "url_photo": "/uploads/rumah/rumah_1.jpg"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

### Get Rumah Detail
Retrieve full details of a house record with photos.

```
GET /api/santri-rumah/{rumah_id}
```

**Path Parameters:**
- `rumah_id` (UUID): Rumah ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Detail rumah berhasil diambil",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "status_rumah": "milik_sendiri",
    "jenis_lantai": "keramik",
    "jenis_dinding": "tembok",
    "jenis_atap": "genteng",
    "akses_air_bersih": "layak",
    "daya_listrik_va": "2200",
    "foto_rumah": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440005",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_1.jpg",
        "url_photo": "/uploads/rumah/rumah_1.jpg"
      },
      {
        "id": "990e8400-e29b-41d4-a716-446655440006",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_2.jpg",
        "url_photo": "/uploads/rumah/rumah_2.jpg"
      }
    ]
  }
}
```

### Get Rumah by Santri
Retrieve house information for a specific santri with photos.

```
GET /api/santri-rumah/santri/{santri_id}
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data rumah berhasil diambil",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "status_rumah": "milik_sendiri",
    "jenis_lantai": "keramik",
    "jenis_dinding": "tembok",
    "jenis_atap": "genteng",
    "akses_air_bersih": "layak",
    "daya_listrik_va": "2200",
    "foto_rumah": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440005",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_1.jpg",
        "url_photo": "/uploads/rumah/rumah_1.jpg"
      }
    ]
  }
}
```

### Create New Rumah
Create a new house record for a santri with optional photos.

```
POST /api/santri-rumah
Content-Type: multipart/form-data
```

**Form Fields:**
```
santri_id: "550e8400-e29b-41d4-a716-446655440000" (required)
status_rumah: "milik_sendiri" (required)
jenis_lantai: "keramik" (required)
jenis_dinding: "tembok" (required)
jenis_atap: "genteng" (required)
akses_air_bersih: "layak" (required)
daya_listrik_va: "2200" (optional)
fotos: [file1.jpg, file2.jpg] (optional, max 5MB each)
```
```

**Status Rumah Options:**
- `milik_sendiri` - Rumah milik sendiri
- `kontrak` - Rumah kontrak
- `menumpang` - Rumah menumpang

**Jenis Lantai Options:**
- `tanah` - Lantai tanah
- `semen` - Lantai semen
- `keramik` - Lantai keramik

**Jenis Dinding Options:**
- `bambu` - Dinding bambu
- `kayu` - Dinding kayu
- `tembok` - Dinding tembok

**Jenis Atap Options:**
- `rumbia` - Atap rumbia
- `seng` - Atap seng
- `genteng` - Atap genteng
- `beton` - Atap beton

**Akses Air Bersih Options:**
- `layak` - Akses air bersih layak
- `tidak_layak` - Akses air bersih tidak layak

**Daya Listrik VA Options:**
- `450` - 450 VA
- `900` - 900 VA
- `1300` - 1300 VA
- `2200` - 2200 VA
- `3500` - 3500 VA
- `5500` - 5500 VA

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Data rumah berhasil ditambahkan",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "status_rumah": "milik_sendiri",
    "jenis_lantai": "keramik",
    "jenis_dinding": "tembok",
    "jenis_atap": "genteng",
    "akses_air_bersih": "layak",
    "daya_listrik_va": "2200",
    "foto_rumah": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440005",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_1.jpg",
        "url_photo": "/uploads/rumah/rumah_1.jpg"
      },
      {
        "id": "990e8400-e29b-41d4-a716-446655440006",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_2.jpg",
        "url_photo": "/uploads/rumah/rumah_2.jpg"
      }
    ]
  }
}
```

### Update Rumah
Update house data with optional new photos (partial update).

```
PUT /api/santri-rumah/{rumah_id}
Content-Type: multipart/form-data
```

**Form Fields:** (all optional)
```
status_rumah: "kontrak"
jenis_lantai: "semen"
jenis_dinding: "tembok"
jenis_atap: "genteng"
akses_air_bersih: "layak"
daya_listrik_va: "1300"
fotos: [file1.jpg, file2.jpg] (optional, max 5MB each)
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data rumah berhasil diupdate",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "status_rumah": "kontrak",
    "jenis_lantai": "semen",
    "jenis_dinding": "tembok",
    "jenis_atap": "genteng",
    "akses_air_bersih": "layak",
    "daya_listrik_va": "1300",
    "foto_rumah": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440005",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_1.jpg",
        "url_photo": "/uploads/rumah/rumah_1.jpg"
      },
      {
        "id": "990e8400-e29b-41d4-a716-446655440007",
        "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
        "nama_file": "rumah_3.jpg",
        "url_photo": "/uploads/rumah/rumah_3.jpg"
      }
    ]
  }
}
```

**Notes:**
- You can update data fields only (without fotos)
- You can add new photos only (without changing data)
- You can do both in a single request
- New photos are added to existing ones (not replaced)

### Delete Rumah
Delete a house record and all related photos.

```
DELETE /api/santri-rumah/{rumah_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data rumah berhasil dihapus",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003"
  }
}
```

### Add Photos to Rumah
Add multiple photos to an existing rumah.

```
POST /api/santri-rumah/{rumah_id}/photos
Content-Type: multipart/form-data
```

**Form Fields:**
```
fotos: [file1.jpg, file2.jpg, ...]
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440005",
      "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
      "nama_file": "rumah_1.jpg",
      "url_photo": "/uploads/rumah/rumah_1.jpg"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440006",
      "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
      "nama_file": "rumah_2.jpg",
      "url_photo": "/uploads/rumah/rumah_2.jpg"
    }
  ]
}
```

### Update Rumah Photo
Replace a rumah photo with a new one.

```
PUT /api/santri-rumah/photos/{foto_id}
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto: file.jpg
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo updated successfully",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440005",
    "rumah_id": "880e8400-e29b-41d4-a716-446655440003",
    "nama_file": "rumah_new.jpg",
    "url_photo": "/uploads/rumah/rumah_new.jpg"
  }
}
```

### Delete Rumah Photo
Delete a single rumah photo.

```
DELETE /api/santri-rumah/photos/{foto_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "message": "Photo deleted successfully"
  }
}
```

---

## Santri Asset (Aset)

### List All Assets
```
GET /api/santri-asset?page=1&per_page=20&santri_id={uuid}
```

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `santri_id` (optional): Filter by santri
- `pesantren_id` (optional, UUID): Filter by pesantren

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "jenis_aset": "motor",
      "jumlah": 1,
      "nilai_perkiraan": 15000000,
      "foto_count": 0
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_items": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Get Asset Detail
```
GET /api/santri-asset/{asset_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "jenis_aset": "motor",
    "jumlah": 1,
    "nilai_perkiraan": 15000000,
    "foto_asset": [
      {
        "id": "880e8400-e29b-41d4-a716-446655440004",
        "asset_id": "770e8400-e29b-41d4-a716-446655440002",
        "nama_file": "motor_1.jpg",
        "url_photo": "/uploads/asset/motor_1.jpg"
      }
    ]
  }
}
```

### Filter Assets by Santri
Use the query parameter `santri_id` on the list endpoint.

```
GET /api/santri-asset?santri_id={uuid}
```

**Response (200 OK):** same as "List All Assets".

### Create Asset
```
POST /api/santri-asset
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_id": "550e8400-e29b-41d4-a716-446655440000",
  "jenis_aset": "motor",
  "jumlah": 1,
  "nilai_perkiraan": 15000000
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "jenis_aset": "motor",
    "jumlah": 1,
    "nilai_perkiraan": 15000000,
    "foto_asset": []
  }
}
```

Notes:
- Valid `jenis_aset`: `motor`, `mobil`, `sepeda`, `hp`, `laptop`, `lahan`, `ternak`, `alat_kerja`, `lainnya`.
- If your UI uses "handphone", map it to `hp` to avoid validation errors.
- Upload photos separately via `POST /api/santri-asset/{asset_id}/photos`.

### Bulk Create Assets (with Photos)
Create multiple assets at once and optionally attach multiple photos for each.

```
POST /api/santri-asset/bulk
Content-Type: multipart/form-data
```

**Form Fields:**
- `assets`: JSON array of objects
- `fotos_{index}`: files for the asset at that array index (e.g., `fotos_0`, `fotos_1`). You can also use alternative prefixes `foto_files_{index}`, `files_{index}`, `foto_asset_{index}`. If you send files without an index (e.g., `fotos`, `foto_files`, `files`, `foto_asset`), they will be attached to the first asset (index 0).

Example `assets` JSON:
```json
[
  {
    "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf",
    "jenis_aset": "hp",
    "jumlah": 1,
    "nilai_perkiraan": 1000000
  },
  {
    "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf",
    "jenis_aset": "motor",
    "jumlah": 1,
    "nilai_perkiraan": 15000000
  }
]
```

- `fotos_0`: files for the first asset (index 0)
- `fotos_1`: files for the second asset (index 1)
- Continue with `fotos_{index}` for each asset in the `assets` array, or use the alternative prefixes noted above.

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440010",
      "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf",
      "jenis_aset": "hp",
      "jumlah": 1,
      "nilai_perkiraan": 1000000,
      "foto_asset": [
        {
          "id": "880e8400-e29b-41d4-a716-446655440100",
          "asset_id": "770e8400-e29b-41d4-a716-446655440010",
          "nama_file": "hp_1.jpg",
          "url_photo": "/uploads/asset/hp_1.jpg"
        }
      ]
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440011",
      "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf",
      "jenis_aset": "motor",
      "jumlah": 1,
      "nilai_perkiraan": 15000000,
      "foto_asset": []
    }
  ],
  "meta": { "created_count": 2 }
}
```

**Curl Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/santri-asset/bulk \
  -F "assets=[{\"santri_id\":\"ae739ebe-2f19-43e1-9244-580bfb8a9acf\",\"jenis_aset\":\"hp\",\"jumlah\":1,\"nilai_perkiraan\":1000000},{\"santri_id\":\"ae739ebe-2f19-43e1-9244-580bfb8a9acf\",\"jenis_aset\":\"motor\",\"jumlah\":1,\"nilai_perkiraan\":15000000}]" \
  -F fotos_0=@hp_1.jpg \
  -F fotos_0=@hp_2.jpg \
  -F fotos_1=@motor_1.jpg
```

**Frontend (Vue/axios) Example:**
```js
const form = new FormData();
const assets = [
  { santri_id, jenis_aset: 'hp', jumlah: 1, nilai_perkiraan: 1000000 },
  { santri_id, jenis_aset: 'motor', jumlah: 1, nilai_perkiraan: 15000000 }
];
form.append('assets', JSON.stringify(assets));

// Attach photos for asset index 0
form.append('fotos_0', fileHp1);
form.append('fotos_0', fileHp2);

// Attach photos for asset index 1
form.append('fotos_1', fileMotor1);

await axios.post('/api/santri-asset/bulk', form);
```

### Update Asset
Update asset data with optional new photos (multipart/form-data).

```
PUT /api/santri-asset/{asset_id}
Content-Type: multipart/form-data
```

**Form Fields:** (all optional)
```
jenis_aset: "mobil"
jumlah: 2
nilai_perkiraan: 50000000
fotos: [file1.jpg, file2.jpg] (optional, max 5MB each)
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "jenis_aset": "mobil",
    "jumlah": 2,
    "nilai_perkiraan": 50000000,
    "foto_asset": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440005",
        "asset_id": "770e8400-e29b-41d4-a716-446655440002",
        "nama_file": "mobil_1.jpg",
        "url_photo": "/uploads/asset/770e8400-e29b-41d4-a716-446655440002/mobil_1.jpg"
      }
    ]
  }
}
```

**Note:** Photos uploaded during update are added to existing photos (not replaced). To replace individual photos, use the update photo endpoint.

### Delete Asset
```
DELETE /api/santri-asset/{asset_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "message": "Asset deleted successfully"
  }
}
```

### Add Photos to Asset
Add multiple photos to an existing asset.

```
POST /api/santri-asset/{asset_id}/photos
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto_files: [file1.jpg, file2.jpg, ...]
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "asset_id": "770e8400-e29b-41d4-a716-446655440002",
      "nama_file": "motor_1.jpg",
      "url_photo": "/uploads/asset/motor_1.jpg"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440005",
      "asset_id": "770e8400-e29b-41d4-a716-446655440002",
      "nama_file": "motor_2.jpg",
      "url_photo": "/uploads/asset/motor_2.jpg"
    }
  ]
}
```

### Update Asset Photo
Replace an asset photo with a new one.

```
PUT /api/santri-asset/photos/{foto_id}
Content-Type: multipart/form-data
```

**Form Fields:**
```
foto: file.jpg
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Photo updated successfully",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440004",
    "asset_id": "770e8400-e29b-41d4-a716-446655440002",
    "nama_file": "motor_new.jpg",
    "url_photo": "/uploads/asset/motor_new.jpg"
  }
}
```

### Delete Asset Photo
Delete a single asset photo.

```
DELETE /api/santri-asset/photos/{foto_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "message": "Photo deleted successfully"
  }
}
```

---

## Santri Bansos (Bantuan Sosial)

### List All Bansos
```
GET /api/santri-bansos?page=1&per_page=20&santri_id={uuid}&pesantren_id={uuid}
```

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `santri_id` (optional): Filter by santri
- `pesantren_id` (optional, UUID): Filter by pesantren

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data bansos berhasil diambil",
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "pkh": true,
      "bpnt": false,
      "pip": true,
      "kis_pbi": false,
      "blt_desa": true,
      "bantuan_lainnya": "Bantuan dari desa"
    }
  ],
  "pagination": { ... }
}
```

### Get Bansos Detail
```
GET /api/santri-bansos/{bansos_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Detail bansos berhasil diambil",
  "data": { ... }
}
```

### Get Bansos by Santri
```
GET /api/santri-bansos/santri/{santri_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data bansos berhasil diambil",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "pkh": true,
    "bpnt": false,
    "pip": true
  }
}
```

### Create Bansos
```
POST /api/santri-bansos
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_id": "550e8400-e29b-41d4-a716-446655440000",
  "pkh": true,
  "bpnt": false,
  "pip": true,
  "kis_pbi": false,
  "blt_desa": true,
  "bantuan_lainnya": "Bantuan dari desa"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Data bansos berhasil ditambahkan",
  "data": { ... }
}
```

### Update Bansos
```
PUT /api/santri-bansos/{bansos_id}
Content-Type: application/json
```

**Request Body:** (all optional)
```json
{
  "pkh": false,
  "pip": false,
  "bantuan_lainnya": "Bantuan dari desa diperbarui"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data bansos berhasil diupdate",
  "data": { ... }
}
```

### Delete Bansos
```
DELETE /api/santri-bansos/{bansos_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data bansos berhasil dihapus",
  "data": { ... }
}
```

---

## Santri Kesehatan (Health)

### List All Health Records
```
GET /api/santri-kesehatan?page=1&per_page=20&santri_id={uuid}&pesantren_id={uuid}
```

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `santri_id` (optional): Filter by santri
- `pesantren_id` (optional, UUID): Filter by pesantren

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data kesehatan berhasil diambil",
  "data": [
    {
      "tinggi_badan": 166,
      "berat_badan": 65,
      "status_gizi": null,
      "riwayat_penyakit": "Tidak ada",
      "alergi_obat": null,
      "kebutuhan_khusus": "Tidak ada",
      "id": "db222f23-e5d2-488b-992e-7695a8aee26f",
      "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf"
    }
  ],
  "pagination": { ... }
}
```

### Get Health Detail
```
GET /api/santri-kesehatan/{kesehatan_id}
```

### Get Health by Santri
```
GET /api/santri-kesehatan/santri/{santri_id}
```

### Create Health Record
```
POST /api/santri-kesehatan
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf",
  "tinggi_badan": 166,
  "berat_badan": 65,
  "status_gizi": null,
  "riwayat_penyakit": "Tidak ada",
  "alergi_obat": null,
  "kebutuhan_khusus": "Tidak ada"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Data kesehatan berhasil ditambahkan",
  "data": {
    "tinggi_badan": 166,
    "berat_badan": 65,
    "status_gizi": null,
    "riwayat_penyakit": "Tidak ada",
    "alergi_obat": null,
    "kebutuhan_khusus": "Tidak ada",
    "id": "db222f23-e5d2-488b-992e-7695a8aee26f",
    "santri_id": "ae739ebe-2f19-43e1-9244-580bfb8a9acf"
  }
}
```

### Update Health Record
```
PUT /api/santri-kesehatan/{kesehatan_id}
Content-Type: application/json
```

**Request Body:** (all optional)
```json
{
  "tinggi_badan": 167,
  "berat_badan": 66,
  "status_gizi": "baik",
  "riwayat_penyakit": "Tidak ada",
  "alergi_obat": "Paracetamol",
  "kebutuhan_khusus": "Tidak ada"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data kesehatan berhasil diupdate",
  "data": { ... }
}
```

### Delete Health Record
```
DELETE /api/santri-kesehatan/{kesehatan_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data kesehatan berhasil dihapus",
  "data": { ... }
}
```

---

## Santri Pembiayaan (Financing)

### List All Financing Records
```
GET /api/santri-pembiayaan?page=1&per_page=20&santri_id={uuid}&pesantren_id={uuid}
```

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `santri_id` (optional): Filter by santri
- `pesantren_id` (optional, UUID): Filter by pesantren

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data pembiayaan berhasil diambil",
  "data": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "biaya_per_bulan": 500000,
      "sumber_biaya": "orang_tua",
      "nama_donatur": null,
      "jenis_beasiswa": null,
      "status_pembayaran": "lancar",
      "tunggakan_bulan": 0,
      "keterangan": "Pembayaran dari orang tua tepat waktu"
    }
  ],
  "pagination": { ... }
}
```

### Get Financing Detail
```
GET /api/santri-pembiayaan/{pembiayaan_id}
```

### Get Financing by Santri
```
GET /api/santri-pembiayaan/santri/{santri_id}
```

### Create Financing Record
```
POST /api/santri-pembiayaan
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_id": "550e8400-e29b-41d4-a716-446655440000",
  "biaya_per_bulan": 500000,
  "sumber_biaya": "orang_tua",
  "status_pembayaran": "lancar",
  "tunggakan_bulan": 0,
  "keterangan": "Pembayaran dari orang tua"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Data pembiayaan berhasil ditambahkan",
  "data": { ... }
}
```

### Update Financing Record
```
PUT /api/santri-pembiayaan/{pembiayaan_id}
Content-Type: application/json
```

**Request Body:** (all optional)
```json
{
  "status_pembayaran": "terlambat",
  "tunggakan_bulan": 1,
  "keterangan": "Pembayaran tertunda 1 bulan"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data pembiayaan berhasil diupdate",
  "data": { ... }
}
```

### Delete Financing Record
```
DELETE /api/santri-pembiayaan/{pembiayaan_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data pembiayaan berhasil dihapus",
  "data": { ... }
}
```

---

## Scoring System

**System Overview:**
This system has two separate scoring modules:
1. **Santri Scoring** (this section) - Assesses poverty level of individual santri
2. **Pesantren Scoring** (see [Pesantren Scoring System](#pesantren-scoring-system)) - Assesses quality/eligibility of pesantren

**Santri Scoring Focus:** Analyzes santri's economic situation, living conditions, assets, and support received.

**Important Notes:**
- ✅ Each scoring calculation is **independent** per santri/pesantren
- ✅ Results are **saved to database** (tables: `santri_skor`, `pesantren_skor`)
- ✅ Can be **re-calculated** anytime when data changes
- ✅ Frontend can **display historical scores** from database
- ✅ No need to recalculate all records when updating one santri/pesantren

**Recent Updates (v1.0.0 - January 2026):**
- ✅ Fixed `status_pembayaran` mapping - now properly scored in pembiayaan dimension
- ✅ Fixed `tunggakan_bulan` mapping - now properly scored in pembiayaan dimension
- ✅ Added NULL handling with `is_null` operator for missing pembiayaan data
- ✅ Added `empty` and `not_empty` operators for string field validation
- ✅ Added direct field mappings for `status_gizi`, `riwayat_penyakit`, `kebutuhan_khusus`
- ✅ Improved scoring accuracy by ensuring all configured parameters are evaluated

**Breaking Changes:**
- ⚠️ **Pembiayaan scores will change** after recalculation due to previously missing fields
- ⚠️ **Recommended**: Recalculate all santri scores to reflect accurate pembiayaan data
- ⚠️ **Example**: Santri with `status_pembayaran="terlambat"` and `tunggakan_bulan=5` now gets +10 points instead of previous incomplete calculation

**Typical Workflow:**
1. **After creating/updating** santri data → Call calculate API
2. **Display scores** → Fetch from database via GET endpoints
3. **Data changed?** → Re-calculate only that specific santri/pesantren
4. **Bulk update?** → Use batch endpoints for efficiency

---

### Calculate Single Santri Score
Calculate poverty score for **ONE specific santri** and save to database. Use this after creating or updating a santri's data.

```
POST /api/scoring/{santri_id}/calculate
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

**Use Case:**
- After creating a new santri
- After updating santri's economic/health/asset data
- When manually re-calculating scores

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Skor berhasil dihitung dan disimpan",
  "data": {
    "skor": {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "skor_ekonomi": 25,
      "skor_rumah": 22,
      "skor_aset": 23,
      "skor_pembiayaan": 2,
      "skor_kesehatan": 0,
      "skor_bansos": 11,
      "skor_total": 83,
      "kategori_kemiskinan": "Sangat Miskin",
      "metode": "pesantren_kemiskinan_v1",
      "version": "1.0.0",
      "calculated_at": "2025-12-28T10:30:45.123Z"
    },
    "breakdown": {
      "dimensi": [
        {
          "nama": "Ekonomi",
          "skor": 25,
          "skor_maks": 40,
          "bobot": 30.0,
          "kontribusi": 7.5,
          "interpretasi": "Sedang",
          "detail": [
            {
              "parameter": "Pendapatan Bulanan",
              "nilai": "800000",
              "skor": 20
            },
            {
              "parameter": "Pekerjaan Orang Tua",
              "nilai": "buruh",
              "skor": 5
            },
            {
              "parameter": "Pendidikan Orang Tua",
              "nilai": "SD",
              "skor": 3
            }
          ]
        },
        {
          "nama": "Kondisi Rumah",
          "skor": 15,
          "skor_maks": 43,
          "bobot": 25.0,
          "kontribusi": 3.75,
          "interpretasi": "Sedang",
          "detail": [
            {
              "parameter": "Status Rumah",
              "nilai": "menumpang",
              "skor": 10
            },
            {
              "parameter": "Jenis Lantai",
              "nilai": "tanah",
              "skor": 10
            }
          ]
        },
        {
          "nama": "Kepemilikan Aset",
          "skor": 10,
          "skor_maks": 23,
          "bobot": 15.0,
          "kontribusi": 1.5,
          "interpretasi": "Baik",
          "detail": [
            {
              "parameter": "Motor",
              "nilai": "0",
              "skor": 5
            },
            {
              "parameter": "HP",
              "nilai": "1",
              "skor": 0
            }
          ]
        },
        {
          "nama": "Pembiayaan Pendidikan",
          "skor": 8,
          "skor_maks": 25,
          "bobot": 15.0,
          "kontribusi": 1.2,
          "interpretasi": "Baik",
          "detail": [
            {
              "parameter": "Sumber Biaya",
              "nilai": "orang_tua",
              "skor": 2
            },
            {
              "parameter": "Status Pembayaran",
              "nilai": "terlambat",
              "skor": 5
            },
            {
              "parameter": "Tunggakan Bulan",
              "nilai": "5",
              "skor": 5
            }
          ]
        },
        {
          "nama": "Kesehatan",
          "skor": 5,
          "skor_maks": 25,
          "bobot": 10.0,
          "kontribusi": 0.5,
          "interpretasi": "Baik",
          "detail": [
            {
              "parameter": "Status Gizi",
              "nilai": "kurang",
              "skor": 10
            },
            {
              "parameter": "Riwayat Penyakit",
              "nilai": "Asma",
              "skor": 8
            },
            {
              "parameter": "Kebutuhan Khusus",
              "nilai": "Tidak ada data",
              "skor": 0
            }
          ]
        },
        {
          "nama": "Penerima Bantuan Sosial",
          "skor": 3,
          "skor_maks": 17,
          "bobot": 5.0,
          "kontribusi": 0.15,
          "interpretasi": "Baik",
          "detail": [
            {
              "parameter": "PKH",
              "nilai": "False",
              "skor": 5
            }
          ]
        }
      ],
      "skor_total": 66,
      "kategori_kemiskinan": "Miskin",
      "interpretasi_kategori": "Kondisi buruk, memerlukan bantuan"
    }
  }
}
```

**Breakdown Fields Explanation:**
- `nama`: Nama dimensi (Ekonomi, Kondisi Rumah, dll)
- `skor`: Skor dimensi (semakin tinggi = kondisi semakin buruk)
- `skor_maks`: Skor maksimal dimensi
- `bobot`: Bobot dimensi dalam persen (30% = 30.0)
- `kontribusi`: Kontribusi ke total skor (skor × bobot ÷ 100)
- `interpretasi`: Interpretasi kondisi dimensi:
  - **Sangat Baik**: Skor 0 (tidak ada masalah)
  - **Baik**: Skor ≤ 25% dari maks (sedikit masalah)
  - **Sedang**: Skor ≤ 50% dari maks (beberapa masalah)
  - **Buruk**: Skor ≤ 75% dari maks (banyak masalah)
  - **Sangat Buruk**: Skor > 75% dari maks (masalah serius)
- `detail`: Array parameter yang berkontribusi ke skor dimensi
- `interpretasi_kategori`: Penjelasan kategori kemiskinan

**Frontend Implementation Example:**
```javascript
// After updating santri data
await axios.put(`/api/santri-pribadi/${santriId}`, updatedData);

// Recalculate score for this specific santri only
const scoreResponse = await axios.post(`/api/scoring/${santriId}/calculate`);
console.log('New score:', scoreResponse.data.data.skor_total);

// Display breakdown to user
const breakdown = scoreResponse.data.data.breakdown;
console.log('Kategori:', breakdown.kategori_kemiskinan);
console.log('Interpretasi:', breakdown.interpretasi_kategori);

// Show dimension details
breakdown.dimensi.forEach(dim => {
  console.log(`${dim.nama}: ${dim.skor}/${dim.skor_maks} (${dim.interpretasi})`);
  console.log(`  Kontribusi: ${dim.kontribusi} poin`);
  
  // Show parameter details
  dim.detail?.forEach(param => {
    console.log(`  - ${param.parameter}: ${param.nilai} (skor: ${param.skor})`);
  });
});
```

### Batch Calculate All Santri
Calculate scores for all santri at once.

```
POST /api/scoring/batch/calculate-all
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Scoring selesai: 150 berhasil, 0 gagal",
  "data": {
    "total_processed": 150,
    "total_errors": 0,
    "results": [
      {
        "santri_id": "550e8400-e29b-41d4-a716-446655440000",
        "nama": "Ahmad Hidayat",
        "skor_total": 66,
        "kategori": "Miskin"
      },
      {
        "santri_id": "550e8400-e29b-41d4-a716-446655440001",
        "nama": "Siti Aisyah",
        "skor_total": 45,
        "kategori": "Rentan"
      }
    ],
    "errors": null
  }
}
```

### Bulk Calculate Asset Scores
Calculate scores for multiple santri at once (useful after adding/updating assets).

```
POST /api/scoring/bulk/calculate-asset
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "metode": "rules.v1",
  "version": "1.0.0"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Bulk scoring selesai: 3 berhasil, 0 gagal",
  "data": {
    "total_requested": 3,
    "total_success": 3,
    "total_errors": 0,
    "results": [
      {
        "santri_id": "550e8400-e29b-41d4-a716-446655440000",
        "skor_total": 66,
        "skor_aset": 10,
        "kategori_kemiskinan": "Miskin",
        "success": true
      },
      {
        "santri_id": "550e8400-e29b-41d4-a716-446655440001",
        "skor_total": 52,
        "skor_aset": 8,
        "kategori_kemiskinan": "Rentan",
        "success": true
      },
      {
        "santri_id": "550e8400-e29b-41d4-a716-446655440002",
        "skor_total": 45,
        "skor_aset": 12,
        "kategori_kemiskinan": "Rentan",
        "success": true
      }
    ],
    "errors": []
  }
}
```

**Curl Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/scoring/bulk/calculate-asset \
  -H "Content-Type: application/json" \
  -d '{
    "santri_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
    "metode": "rules.v1",
    "version": "1.0.0"
  }'
```

**Frontend (Vue/axios) Example:**
```js
await axios.post('/api/scoring/bulk/calculate-asset', {
  santri_ids: [
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001'
  ],
  metode: 'rules.v1',
  version: '1.0.0'
});
```

### Get Score by Santri ID
Retrieve **latest saved score** for a santri from database. Returns the most recent calculation.

```
GET /api/scoring/santri/{santri_id}
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

**Use Case:**
- Display score on santri detail page
- Show score in santri list/table
- Check current poverty status

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "skor_ekonomi": 25,
    "skor_rumah": 15,
    "skor_aset": 10,
    "skor_pembiayaan": 8,
    "skor_kesehatan": 5,
    "skor_bansos": 3,
    "skor_total": 66,
    "kategori_kemiskinan": "Miskin",
    "metode": "pesantren_kemiskinan_v1",
    "version": "1.0.0",
    "calculated_at": "2025-12-28T10:30:45.123Z",
    "breakdown": {
      "dimensi": [
        {
          "nama": "Ekonomi",
          "skor": 25,
          "skor_maks": 40,
          "bobot": 30.0,
          "kontribusi": 7.5,
          "interpretasi": "Sedang",
          "detail": [
            {
              "parameter": "Pendapatan Bulanan",
              "nilai": "800000",
              "skor": 20
            },
            {
              "parameter": "Pekerjaan Orang Tua",
              "nilai": "buruh",
              "skor": 5
            }
          ]
        }
      ],
      "skor_total": 66,
      "kategori_kemiskinan": "Miskin",
      "interpretasi_kategori": "Kondisi buruk, memerlukan bantuan"
    }
  }
}
```

**Note:** Response includes `breakdown` field with detailed scoring information for each dimension.

**Frontend Implementation Example:**
```javascript
// Display score on santri profile page
const { data } = await axios.get(`/api/scoring/santri/${santriId}`);
if (data.success) {
  displayScore(data.data.skor_total);
  displayCategory(data.data.kategori_kemiskinan);
  displayBreakdown({
    ekonomi: data.data.skor_ekonomi,
    rumah: data.data.skor_rumah,
    aset: data.data.skor_aset
  });
}
```
    "calculated_at": "2025-12-28T10:30:45.123Z"
  }
}
```

### Get Score by ID
Retrieve a specific score record.

```
GET /api/scoring/{skor_id}
```

**Path Parameters:**
- `skor_id` (UUID): Score record ID

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

### Scoring Categories

Based on `scoring.json` configuration:

| Skor Total | Kategori |
|-----------|----------|
| ≥ 80 | Sangat Miskin |
| 65 - 79 | Miskin |
| 45 - 64 | Rentan |
| < 45 | Tidak Miskin |

### Scoring Dimensions & Weights

| Dimensi | Bobot | Skor Maks | Parameters |
|---------|-------|-----------|-----------|
| Ekonomi | 30% | 40 | pendapatan_bulanan (orangtua), pekerjaan (orangtua), pendidikan (orangtua) |
| Rumah | 25% | 43 | status_rumah, jenis_lantai, jenis_dinding, jenis_atap, akses_air_bersih, daya_listrik_va |
| Aset | 15% | 23 | motor, mobil, lahan, hp, ternak, sepeda, laptop, alat_kerja, lainnya (count per jenis aset) |
| Pembiayaan | 15% | 25 | sumber_biaya, status_pembayaran, tunggakan_bulan |
| Kesehatan | 10% | 25 | status_gizi, riwayat_penyakit, kebutuhan_khusus |
| Bansos | 5% | 17 | pkh, bpnt, pip, kis_pbi, blt_desa (false = skor tinggi, belum menerima bantuan) |

**Key Scoring Logic:**
- **Ekonomi**: Pendapatan < 500K = 30 poin, Pekerjaan buruh/petani = 5 poin, Pendidikan SD/tidak sekolah = 5 poin
- **Rumah**: Status menumpang = 10 poin, Lantai tanah = 10 poin, Dinding bambu = 8 poin, Listrik 450VA = 8 poin
- **Aset**: Tidak punya motor/mobil/lahan/HP/ternak/sepeda/laptop/alat_kerja/lainnya = skor tinggi (kemiskinan)
- **Pembiayaan**: 
  - Sumber donatur = 10 poin, beasiswa = 8 poin, wali = 5 poin, orang_tua = 2 poin
  - Status menunggak = 10 poin, terlambat = 5 poin, lancar = 0 poin, NULL = 3 poin
  - Tunggakan ≥3 bulan = 5 poin, ≥1 bulan = 3 poin, 0 bulan = 0 poin, NULL = 2 poin
- **Kesehatan**: 
  - Status gizi kurang = 10 poin, lebih = 5 poin, baik = 0 poin
  - Riwayat penyakit ada (not empty) = 8 poin, tidak ada (empty) = 0 poin
  - Kebutuhan khusus ada (not empty) = 7 poin, tidak ada (empty) = 0 poin
- **Bansos**: Belum menerima PKH/PIP/BPNT/KIS = skor tinggi (indikator perlu bantuan)

### Scoring Operators

Sistem scoring mendukung operator berikut untuk evaluasi rules:

| Operator | Deskripsi | Contoh Penggunaan |
|----------|-----------|-------------------|
| `==` | Sama dengan (equality) | `status_pembayaran == "lancar"` |
| `<` | Kurang dari | `pendapatan_bulanan < 500000` |
| `<=` | Kurang dari atau sama dengan | `pendapatan_bulanan <= 1000000` |
| `>=` | Lebih dari atau sama dengan | `tunggakan_bulan >= 3` |
| `in` | Nilai ada dalam list | `pekerjaan in ["buruh", "petani"]` |
| `is_null` | Nilai NULL atau kosong | `status_pembayaran is_null` |
| `empty` | String kosong atau NULL | `riwayat_penyakit empty` |
| `not_empty` | String tidak kosong | `riwayat_penyakit not_empty` |

**NULL Handling:**
- Jika field pembiayaan/kesehatan NULL, sistem memberikan skor default (moderate risk)
- `status_pembayaran` NULL → 3 poin (antara lancar dan terlambat)
- `tunggakan_bulan` NULL → 2 poin (asumsi risiko sedang)
- Field lain yang NULL → 0 poin (tidak berkontribusi ke skor)

**Important Notes:**
- ✅ **Latest Version (v1.0.0)**: Includes NULL handling and comprehensive field mapping
- ✅ **Data Validation**: Ensure pembiayaan and kesehatan data is complete for accurate scoring
- ✅ **Recalculate Required**: After updating pembiayaan/kesehatan data, call calculate API to refresh scores

**Example: Pembiayaan Scoring Calculation**

Given this data:
```json
{
  "sumber_biaya": "orang_tua",
  "status_pembayaran": "terlambat",
  "tunggakan_bulan": 5
}
```

Calculation:
- `sumber_biaya="orang_tua"` → 2 points
- `status_pembayaran="terlambat"` → 5 points
- `tunggakan_bulan=5` (≥3) → 5 points
- **Total Pembiayaan Score: 12/25**

**Example: NULL Handling**

Given incomplete data:
```json
{
  "sumber_biaya": "beasiswa",
  "status_pembayaran": null,
  "tunggakan_bulan": null
}
```

Calculation:
- `sumber_biaya="beasiswa"` → 8 points
- `status_pembayaran=null` → 3 points (moderate risk default)
- `tunggakan_bulan=null` → 2 points (moderate risk default)
- **Total Pembiayaan Score: 13/25**

This ensures santri with missing data still get reasonable risk assessment.

---

## Pondok Pesantren (Main Data)

### List Pondok Pesantren
Get paginated list of pesantren with filters.

```
GET /pondok-pesantren?page=1&per_page=20&search=&provinsi=&kabupaten=
```

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20) - Items per page
- `search` (string, optional) - Search by nama or nsp
- `provinsi` (string, optional) - Filter by province
- `kabupaten` (string, optional) - Filter by regency

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid",
      "nama": "Pondok Pesantren Al-Ikhlas",
      "nsp": "12345678",
      "alamat": "Jl. Raya No. 123",
      "kabupaten": "Tasikmalaya",
      "provinsi": "Jawa Barat",
      "nama_kyai": "KH. Ahmad",
      "jumlah_santri": 500,
      "jumlah_guru": 25,
      "tahun_berdiri": 1985
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

### Get Pesantren Detail
```
GET /pondok-pesantren/{pesantren_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "nama": "Pondok Pesantren Al-Ikhlas",
  "nsp": "12345678",
  "alamat": "Jl. Raya No. 123",
  "desa": "Cikunir",
  "kecamatan": "Singaparna",
  "kabupaten": "Tasikmalaya",
  "provinsi": "Jawa Barat",
  "kode_pos": "46415",
  "latitude": -7.456,
  "longitude": 108.123,
  "telepon": "081234567890",
  "email": "info@pesantren.com",
  "website": "www.pesantren.com",
  "nama_kyai": "KH. Ahmad",
  "jumlah_santri": 500,
  "jumlah_guru": 25,
  "tahun_berdiri": 1985,
  "foto_path": "/uploads/pesantren/{id}/main.jpg",
  "foto_pesantren": [
    {
      "id": "uuid",
      "nama_file": "gallery1.jpg",
      "url_photo": "/uploads/pesantren/{id}/gallery1.jpg"
    }
  ],
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### Dropdown List (for UI selects)
Get all pesantren as a simple list for dropdowns.

```
GET /pondok-pesantren/dropdown
```

**Response (200 OK):**
```json
[
  { "id": "uuid", "nama": "Pondok Pesantren Al-Ikhlas" },
  { "id": "uuid", "nama": "Pondok Pesantren Mahasina" }
]
```

**Optional Search:**
Filter by name, NSP, kabupaten, or provinsi (case-insensitive substring):

```
GET /pondok-pesantren/dropdown?search=mahasina
```

**Filtered Response:**
```json
[
  { "id": "uuid", "nama": "Pondok Pesantren Mahasina" }
]
```

### Photos
- `foto_path`: main photo path for a pesantren.
- `foto_pesantren`: array of gallery photos.
- Images are accessible via `/uploads/...`.

### Create Pesantren
```
POST /pondok-pesantren
```

**Request Body:**
```json
{
  "nama": "Pondok Pesantren Al-Ikhlas",
  "nsp": "12345678",
  "alamat": "Jl. Raya No. 123",
  "desa": "Cikunir",
  "kecamatan": "Singaparna",
  "kabupaten": "Tasikmalaya",
  "provinsi": "Jawa Barat",
  "kode_pos": "46415",
  "longitude": 108.123,
  "latitude": -7.456,
  "telepon": "081234567890",
  "email": "info@pesantren.com",
  "website": "www.pesantren.com",
  "nama_kyai": "KH. Ahmad",
  "jumlah_santri": 500,
  "jumlah_guru": 25,
  "tahun_berdiri": 1985
}
```

**Response (201 Created):** Same as detail response

### Update Pesantren
```
PUT /pondok-pesantren/{pesantren_id}
```

**Request Body:** Same as create (all fields optional)

**Response (200 OK):** Same as detail response

### Delete Pesantren
```
DELETE /pondok-pesantren/{pesantren_id}
```

**Response (204 No Content)**

---

## Pesantren Fisik (Physical Infrastructure)

### Get Fisik by Pesantren ID
```
GET /pesantren-fisik/pesantren/{pesantren_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "pesantren_id": "uuid",
  "luas_tanah": 5000.0,
  "luas_bangunan": 3000.0,
  "kondisi_bangunan": "permanen",
  "status_bangunan": "milik_sendiri",
  "rasio_kepadatan_kamar": 5.5,
  "sanitasi": "layak",
  "air_bersih": "lancar",
  "sumber_air": "PDAM",
  "kualitas_air_bersih": "layak_minum",
  "fasilitas_mck": "lengkap",
  "jumlah_mck": 20,
  "keamanan_bangunan": "tinggi",
  "sistem_keamanan": "CCTV dan satpam 24 jam",
  "jenis_lantai": "keramik",
  "jenis_dinding": "tembok",
  "jenis_atap": "genteng_tanah_liat",
  "sumber_listrik": "PLN",
  "daya_listrik_va": "5500",
  "kestabilan_listrik": "stabil"
}
```

### Get Fisik by ID
```
GET /pesantren-fisik/{fisik_id}
```

**Response (200 OK):** Same as above

### Create Fisik Data
```
POST /pesantren-fisik
```

**Request Body:**
```json
{
  "pesantren_id": "uuid",
  "luas_tanah": 5000.0,
  "luas_bangunan": 3000.0,
  "kondisi_bangunan": "permanen",
  "status_bangunan": "milik_sendiri",
  "rasio_kepadatan_kamar": 5.5,
  "sanitasi": "layak",
  "air_bersih": "lancar",
  "sumber_air": "PDAM",
  "kualitas_air_bersih": "layak_minum",
  "fasilitas_mck": "lengkap",
  "jumlah_mck": 20,
  "keamanan_bangunan": "tinggi",
  "sistem_keamanan": "CCTV dan satpam 24 jam",
  "jenis_lantai": "keramik",
  "jenis_dinding": "tembok",
  "jenis_atap": "genteng_tanah_liat",
  "sumber_listrik": "PLN",
  "daya_listrik_va": "5500",
  "kestabilan_listrik": "stabil"
}
```

**Required Fields:**
- `pesantren_id` (UUID)
- `kondisi_bangunan` (permanen/semi_permanen/non_permanen)
- `rasio_kepadatan_kamar` (float, must be >= 0)
- `sanitasi` (layak/cukup/tidak_layak)
- `air_bersih` (lancar/terbatas/tidak_tersedia)
- `keamanan_bangunan` (tinggi/standar/minim/tidak_aman)
- `jenis_lantai` (marmer/keramik/beton/kayu/tanah)
- `jenis_atap` (genteng_tanah_liat/metal/upvc/seng/asbes/ijuk)
- `jenis_dinding` (tembok/papan/kayu/bambu/anyaman)

**Optional Fields:**
- `luas_tanah` (float, dalam m²)
- `luas_bangunan` (float, dalam m²)
- `status_bangunan` (milik_sendiri/wakaf/hibah/pinjam/sewa)
- `sumber_air` (PDAM/sumur/berbagai_macam/hujan/sungai)
- `kualitas_air_bersih` (layak_minum/keruh/berbau/asin)
- `fasilitas_mck` (lengkap/cukup/kurang_lengkap/tidak_layak)
- `jumlah_mck` (integer, jumlah MCK)
- `sistem_keamanan` (string, deskripsi sistem keamanan)
- `sumber_listrik` (PLN/genset/listrik_tidak_ada/tenaga_surya)
- `daya_listrik_va` (string, contoh: "450", "900", "1300", "2200", "3500", "5500")
- `kestabilan_listrik` (stabil/tidak_stabil/tidak_ada)

**Response (201 Created):** Same as detail response

**Note:** Only one fisik record per pesantren is allowed.

### Update Fisik Data
```
PUT /pesantren-fisik/{fisik_id}
```

**Request Body:** Same as create (all fields optional)

**Response (200 OK):** Same as detail response

### Delete Fisik Data
```
DELETE /pesantren-fisik/{fisik_id}
```

**Response (204 No Content)**

---

## Pesantren Fasilitas (Facilities)

**Note:** This module focuses on educational and support facilities. Infrastructure-related facilities like MCK, water, and electricity are managed in `/pesantren-fisik`. Payment methods are managed in `/pesantren-pendidikan`.

### Get Fasilitas by Pesantren ID
```
GET /pesantren-fasilitas/pesantren/{pesantren_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "pesantren_id": "uuid",
  "jumlah_kamar": 50,
  "jumlah_ruang_kelas": 20,
  "jumlah_masjid": 1,
  "perpustakaan": true,
  "laboratorium": true,
  "ruang_komputer": true,
  "koperasi": true,
  "kantin": true,
  "fasilitas_olahraga": "lapangan_futsal,basket",
  "fasilitas_kesehatan": "klinik",
  "fasilitas_mengajar": "projector,whiteboard",
  "fasilitas_komunikasi": "internet,telepon",
  "akses_transportasi": "angkutan_umum",
  "jarak_ke_kota_km": 5.5,
  "asrama": "layak",
  "ruang_belajar": "layak",
  "internet": "stabil",
  "fasilitas_transportasi": "angkutan_umum",
  "akses_jalan": "aspal"
}
```

### Get Fasilitas by ID
```
GET /pesantren-fasilitas/{fasilitas_id}
```

**Response (200 OK):** Same as above

### Create Fasilitas Data
```
POST /pesantren-fasilitas
```

**Request Body:** (all fields optional except pesantren_id)
```json
{
  "pesantren_id": "uuid",
  "jumlah_kamar": 50,
  "jumlah_ruang_kelas": 20,
  "jumlah_masjid": 1,
  "perpustakaan": true,
  "laboratorium": true,
  "ruang_komputer": true,
  "koperasi": true,
  "kantin": true,
  "fasilitas_olahraga": "lapangan_futsal,basket",
  "fasilitas_kesehatan": "klinik",
  "fasilitas_mengajar": "projector,whiteboard",
  "fasilitas_komunikasi": "internet,telepon",
  "akses_transportasi": "angkutan_umum",
  "jarak_ke_kota_km": 5.5,
  "asrama": "layak",
  "ruang_belajar": "layak",
  "internet": "stabil",
  "fasilitas_transportasi": "bus",
  "akses_jalan": "aspal"
}
```

**Required Enum Values:**
- `asrama`: **layak**, cukup, tidak_layak
- `ruang_belajar`: **layak**, cukup, tidak_layak
- `internet`: **stabil**, tidak_stabil, tidak_ada
- `fasilitas_transportasi`: **bus**, angkutan_umum, kendaraan_pribadi, ojek
- `akses_jalan`: **aspal**, cor_block, tanah, kerikil

**Response (201 Created):** Same as detail response

**Note:** Only one fasilitas record per pesantren is allowed.

### Update Fasilitas Data
```
PUT /pesantren-fasilitas/{fasilitas_id}
```

**Request Body:** (all fields optional)
```json
{
  "jumlah_kamar": 50,
  "jumlah_ruang_kelas": 20,
  "jumlah_masjid": 1,
  "perpustakaan": true,
  "laboratorium": true,
  "ruang_komputer": true,
  "koperasi": true,
  "kantin": true,
  "fasilitas_olahraga": "lapangan_futsal,basket",
  "fasilitas_kesehatan": "klinik",
  "fasilitas_mengajar": "projector,whiteboard",
  "fasilitas_komunikasi": "internet,telepon",
  "akses_transportasi": "angkutan_umum",
  "jarak_ke_kota_km": 5.5,
  "asrama": "layak",
  "ruang_belajar": "cukup",
  "internet": "stabil",
  "fasilitas_transportasi": "angkutan_umum",
  "akses_jalan": "aspal"
}
```

**Valid Enum Values:**
- `asrama`: layak, cukup, tidak_layak
- `ruang_belajar`: layak, cukup, tidak_layak
- `internet`: stabil, tidak_stabil, tidak_ada
- `fasilitas_transportasi`: bus, angkutan_umum, kendaraan_pribadi, ojek
- `akses_jalan`: aspal, cor_block, tanah, kerikil

**Response (200 OK):** Same as detail response

**Note:** `metode_pembayaran` is managed in `/pesantren-pendidikan` module.

**Note:** Fields `fasilitas_mck` and `listrik` (sumber_listrik/kestabilan_listrik) are managed in `pesantren_fisik` module to avoid duplication.

### Delete Fasilitas Data
```
DELETE /pesantren-fasilitas/{fasilitas_id}
```

**Response (204 No Content)**

---

## Pesantren Pendidikan (Education)

### Get Pendidikan by Pesantren ID
```
GET /pesantren-pendidikan/pesantren/{pesantren_id}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "pesantren_id": "uuid",
  "jenjang_pendidikan": "semua_ra_ma",
  "kurikulum": "terstandar",
  "akreditasi": "a",
  "jumlah_guru_tetap": 20,
  "jumlah_guru_tidak_tetap": 5,
  "guru_s1_keatas": 18,
  "persen_guru_bersertifikat": 90,
  "rasio_guru_santri": 1.2,
  "prestasi_akademik": "nasional",
  "prestasi_non_akademik": "regional",
  "prestasi_santri": "nasional",
  "program_unggulan": "Tahfidz,Bahasa Arab",
  "fasilitas_mengajar": "projector,whiteboard",
  "metode_pembayaran": "tunai,non_tunai",
  "biaya_bulanan_min": 200000,
  "biaya_bulanan_max": 500000
}
```

### Get Pendidikan by ID
```
GET /pesantren-pendidikan/{pendidikan_id}
```

**Response (200 OK):** Same as above

### Create Pendidikan Data
```
POST /pesantren-pendidikan
```

**Request Body:** (all fields optional except pesantren_id)
```json
{
  "pesantren_id": "uuid",
  "jenjang_pendidikan": "semua_ra_ma",
  "kurikulum": "terstandar",
  "akreditasi": "a",
  "jumlah_guru_tetap": 20,
  "jumlah_guru_tidak_tetap": 5,
  "guru_s1_keatas": 18,
  "persen_guru_bersertifikat": 90,
  "rasio_guru_santri": 1.2,
  "prestasi_akademik": "nasional",
  "prestasi_non_akademik": "regional",
  "prestasi_santri": "nasional",
  "program_unggulan": "Tahfidz,Bahasa Arab",
  "fasilitas_mengajar": "projector,whiteboard",
  "metode_pembayaran": "tunai,non_tunai",
  "biaya_bulanan_min": 200000,
  "biaya_bulanan_max": 500000
}
```

**Response (201 Created):** Same as detail response

**Response (201 Created):** Same as detail response

**Jenjang Pendidikan Options:**
- `semua_ra_ma` - Semua Ada dari RA-MA
- `pendidikan_dasar` - Pendidikan Dasar Saja (MI)
- `dasar_menengah_pertama` - Pendidikan Dasar hingga Menengah Pertama (MI-MTs)
- `dasar_menengah_atas` - Pendidikan Dasar - Menengah Atas (MI-MA)
- `satu_jenjang` - Hanya satu jenjang Pendidikan

**Valid Enum Values:**
- `kurikulum`: "terstandar", "internal", "tidak_jelas"
- `akreditasi`: "a", "b", "c", "belum" (lowercase only!)
- `prestasi_santri`: "nasional", "regional", "tidak_ada" (NOT "baik"!)
- `prestasi_akademik` & `prestasi_non_akademik`: Free text (recommended: "nasional", "regional", "tidak_ada")
- `fasilitas_mengajar`: Free text, comma-separated (e.g., "projector,whiteboard")
- `metode_pembayaran`: Free text, comma-separated (e.g., "tunai,non_tunai")

**Note:** Only one pendidikan record per pesantren is allowed.

### Update Pendidikan Data
```
PUT /pesantren-pendidikan/{pendidikan_id}
```

**Request Body:** (all fields optional)
```json
{
  "jenjang_pendidikan": "dasar_menengah_pertama",
  "kurikulum": "terstandar",
  "akreditasi": "a",
  "jumlah_guru_tetap": 20,
  "jumlah_guru_tidak_tetap": 5,
  "guru_s1_keatas": 18,
  "persen_guru_bersertifikat": 90,
  "rasio_guru_santri": 1.2,
  "prestasi_akademik": "nasional",
  "prestasi_non_akademik": "regional",
  "prestasi_santri": "nasional",
  "program_unggulan": "Tahfidz,Bahasa Arab",
  "fasilitas_mengajar": "projector,whiteboard",
  "metode_pembayaran": "tunai,non_tunai",
  "biaya_bulanan_min": 200000,
  "biaya_bulanan_max": 500000
}
```

**Response (200 OK):** Same as detail response

### Delete Pendidikan Data
```
DELETE /pesantren-pendidikan/{pendidikan_id}
```

**Response (204 No Content)**

---

## Pesantren Scoring System

**System Purpose:**
Assesses the quality, facilities, and educational standards of pesantren (boarding schools). This is separate from Santri Scoring which assesses individual santri poverty levels.

**Important Notes:**
- ✅ Each pesantren score calculation is **independent** - calculating one pesantren doesn't affect others
- ✅ Results are **saved to database** in the `pesantren_skor` table
- ✅ Can be **re-calculated anytime** when pesantren data changes (fisik, fasilitas, or pendidikan)
- ✅ Frontend can **display saved scores** from database without recalculating
- ✅ No need to recalculate all pesantren when updating just one

**Typical Workflow:**
1. After creating/updating pesantren data → Call calculate API for **that specific pesantren only**
2. Display scores → Fetch from database via GET endpoints (shows **latest saved calculation**)
3. Data changed? → Re-calculate only **that one pesantren** without affecting others
4. Need all scores updated? → Use batch endpoint (useful for initial setup or bulk updates)

**Field Organization for Scoring:**
- **Kelayakan Fisik**: Data from `/pesantren-fisik`
- **Air & Sanitasi**: Data from `/pesantren-fisik` (sanitasi, sumber_air, kualitas_air_bersih, fasilitas_mck)
- **Fasilitas Pendukung**: Data from `/pesantren-fisik` (listrik, akses_jalan) and `/pesantren-fasilitas` (fasilitas_transportasi)
- **Mutu Pendidikan**: Data from `/pesantren-pendidikan` (jenjang_pendidikan, kurikulum, akreditasi, prestasi_santri)

### Calculate Single Pesantren Score
Calculate and save quality score for **one specific pesantren** only.

**Use Case:**
- After creating new pesantren data (fisik, fasilitas, pendidikan)
- After updating any pesantren-related data
- To refresh score when data corrections are made
- Calculate independently without affecting other pesantren records

```
POST /api/pesantren-scoring/{pesantren_id}/calculate
```

**Frontend Implementation Example:**
```javascript
// After updating pesantren fisik data
await axios.put(`/api/pesantren-fisik/${fisikId}`, updatedFisikData);

// Recalculate score for this specific pesantren only
const scoreResponse = await axios.post(`/api/pesantren-scoring/${pesantrenId}/calculate`);
if (scoreResponse.data.success) {
  displayScore(scoreResponse.data.data.skor_total);
  displayCategory(scoreResponse.data.data.kategori_kelayakan);
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Skor pesantren berhasil dihitung dan disimpan",
  "data": {
    "skor": {
      "id": "uuid",
      "pesantren_id": "uuid",
      "skor_fisik": 98,
      "skor_air_sanitasi": 100,
      "skor_fasilitas_pendukung": 83,
      "skor_mutu_pendidikan": 93,
      "skor_total": 94,
      "kategori_kelayakan": "sangat_layak",
      "metode": "pondok_pesantren.rules",
      "version": "1.1",
      "calculated_at": "2025-12-28T10:30:00"
    },
    "breakdown": {
      "dimensi": [
        {
          "nama": "Kelayakan Fisik Bangunan",
          "skor": 98,
          "skor_maks": 100,
          "bobot": 40.0,
          "kontribusi": 39.2,
          "interpretasi": "Sangat Baik",
          "detail": [
            {
              "parameter": "Kondisi Bangunan",
              "nilai": "Permanen",
              "skor": 100
            },
            {
              "parameter": "Status Bangunan",
              "nilai": "Milik Sendiri",
              "skor": 100
            },
            {
              "parameter": "Keamanan Bangunan",
              "nilai": "Tinggi",
              "skor": 100
            },
            {
              "parameter": "Jenis Lantai",
              "nilai": "Keramik",
              "skor": 90
            },
            {
              "parameter": "Jenis Dinding",
              "nilai": "Tembok",
              "skor": 100
            },
            {
              "parameter": "Jenis Atap",
              "nilai": "Genteng Tanah Liat",
              "skor": 100
            }
          ]
        },
        {
          "nama": "Air Bersih dan Sanitasi",
          "skor": 100,
          "skor_maks": 100,
          "bobot": 25.0,
          "kontribusi": 25.0,
          "interpretasi": "Sangat Baik",
          "detail": [
            {
              "parameter": "Air Bersih",
              "nilai": "Lancar",
              "skor": 100
            },
            {
              "parameter": "Sumber Air",
              "nilai": "PDAM",
              "skor": 100
            },
            {
              "parameter": "Sanitasi",
              "nilai": "Layak",
              "skor": 100
            }
          ]
        },
        {
          "nama": "Fasilitas Pendukung",
          "skor": 83,
          "skor_maks": 100,
          "bobot": 20.0,
          "kontribusi": 16.6,
          "interpretasi": "Baik",
          "detail": [
            {
              "parameter": "Sumber Listrik",
              "nilai": "PLN",
              "skor": 100
            },
            {
              "parameter": "Kestabilan Listrik",
              "nilai": "Stabil",
              "skor": 100
            },
            {
              "parameter": "Fasilitas Mengajar",
              "nilai": "Cukup Lengkap",
              "skor": 70
            },
            {
              "parameter": "Akses Jalan",
              "nilai": "Aspal",
              "skor": 100
            }
          ]
        },
        {
          "nama": "Mutu Pendidikan",
          "skor": 93,
          "skor_maks": 100,
          "bobot": 15.0,
          "kontribusi": 13.95,
          "interpretasi": "Sangat Baik",
          "detail": [
            {
              "parameter": "Jenjang Pendidikan",
              "nilai": "Semua Ra Ma",
              "skor": 100
            },
            {
              "parameter": "Kurikulum",
              "nilai": "Terstandar",
              "skor": 100
            },
            {
              "parameter": "Akreditasi",
              "nilai": "A",
              "skor": 100
            },
            {
              "parameter": "Prestasi Santri",
              "nilai": "Regional",
              "skor": 75
            }
          ]
        }
      ],
      "skor_total": 94,
      "kategori_kelayakan": "sangat_layak",
      "interpretasi_kategori": "Kondisi sangat baik, memenuhi semua standar kelayakan"
    }
  }
}
```

**Breakdown Fields Explanation:**
- `nama`: Nama dimensi dengan format friendly
- `skor`: Skor dimensi (0-100, semakin tinggi semakin baik)
- `skor_maks`: Skor maksimal dimensi (selalu 100)
- `bobot`: Bobot dimensi dalam persen (40.0 = 40%)
- `kontribusi`: Kontribusi ke skor total (skor × bobot ÷ 100)
- `interpretasi`: Interpretasi kondisi dimensi:
  - **Sangat Baik**: Skor ≥ 85
  - **Baik**: Skor 70-84
  - **Cukup**: Skor 55-69
  - **Kurang**: Skor < 55
- `detail`: Array parameter yang berkontribusi ke skor dimensi
  - `parameter`: Nama parameter yang dinilai
  - `nilai`: Nilai aktual dari data pesantren
  - `skor`: Skor yang didapat untuk parameter ini (0-100)
- `interpretasi_kategori`: Penjelasan lengkap kategori kelayakan pesantren

**Scoring Dimensions & Calculation:**

The `skor_total` is calculated as **weighted average** of dimension scores:
- Formula: `skor_total = Σ(skor_dimensi × bobot_dimensi)`
- Each dimension score ranges from 0-100 (higher = better condition)
- Final total score ranges from 0-100

**Dimensions:**

1. **Kelayakan Fisik Bangunan (40%)**
   - Parameters: kondisi_bangunan, status_bangunan, keamanan_bangunan, jenis_lantai, jenis_dinding, jenis_atap
   - Data source: `pesantren_fisik` table
   - Evaluates physical structure quality and safety

2. **Air Bersih dan Sanitasi (25%)**
   - Parameters: air_bersih, sumber_air, kualitas_air, sanitasi
   - Data source: `pesantren_fisik` table
   - Evaluates water access and sanitation facilities

3. **Fasilitas Pendukung (20%)**
   - Parameters: sumber_listrik, kestabilan_listrik, fasilitas_mengajar, fasilitas_komunikasi, fasilitas_transportasi, akses_jalan
   - Data source: `pesantren_fisik` and `pesantren_fasilitas` tables
   - Evaluates supporting facilities and accessibility

4. **Mutu Pendidikan (15%)**
   - Parameters: jenjang_pendidikan, kurikulum, akreditasi, prestasi_santri
   - Data source: `pesantren_pendidikan` table
   - Evaluates educational quality and achievements

**Mutu Pendidikan Parameters:**
- `jenjang_pendidikan`: Kelengkapan jenjang (semua_ra_ma: 100, dasar_menengah_atas: 90, dasar_menengah_pertama: 75, pendidikan_dasar: 60, satu_jenjang: 50)
- `kurikulum`: Standardisasi kurikulum (terstandar: 100, internal: 75, tidak_jelas: 40)
- `akreditasi`: Status akreditasi (a: 100, b: 80, c: 60, belum: 40)
- `prestasi_santri`: Tingkat prestasi (nasional: 100, regional: 75, tidak_ada: 40)

**Kategori Kelayakan:**

| Skor Total | Kategori | Interpretasi |
|-----------|----------|-------------|
| ≥ 85 | sangat_layak | Kondisi sangat baik, memenuhi semua standar kelayakan |
| 70-84 | layak | Kondisi baik, memenuhi standar kelayakan |
| 55-69 | cukup_layak | Kondisi cukup, perlu perbaikan di beberapa aspek |
| < 55 | tidak_layak | Kondisi kurang baik, memerlukan perbaikan menyeluruh |

**Dimension Score Interpretation:**
- **Sangat Baik**: 85-100 (Excellent)
- **Baik**: 70-84 (Good)
- **Cukup**: 55-69 (Fair)
- **Kurang**: < 55 (Poor)

### Get Score by Pesantren ID
Retrieve **latest saved score** for a pesantren from database (no calculation performed).

**Use Case:**
- Display score on pesantren detail page
- Show scores in pesantren list/table
- Check facility quality status
- Compare pesantren scores

```
GET /api/pesantren-scoring/pesantren/{pesantren_id}
```

**Response (200 OK):** Same as calculate response

**Frontend Implementation Example:**
```javascript
// Display pesantren score on detail page
const { data } = await axios.get(`/api/pesantren-scoring/pesantren/${pesantrenId}`);

if (data.success) {
  displayScore(data.data.skor_total);
  displayCategory(data.data.kategori_kelayakan);
  
  // Show detailed breakdown
  displayBreakdown({
    fisik: data.data.skor_kelayakan_fisik,
    airSanitasi: data.data.skor_air_sanitasi,
    fasilitas: data.data.skor_fasilitas_pendukung,
    pendidikan: data.data.skor_mutu_pendidikan
  });
}
```

### Get Score by Score ID
```
GET /api/pesantren-scoring/{skor_id}
```

**Response (200 OK):** Same as calculate response

### Batch Calculate All Scores
Calculate scores for all pesantren in the system.

```
POST /api/pesantren-scoring/batch/calculate-all
```

**Response (200 OK):**
```json
{
  "total_processed": 50,
  "total_success": 48,
  "total_failed": 2,
  "results": [
    {
      "pesantren_id": "uuid",
      "status": "success",
      "skor_total": 83
    },
    {
      "pesantren_id": "uuid",
      "status": "failed",
      "error": "Missing required data"
    }
  ]
}
```

---

## Santri Map GIS

**Purpose:** Specialized endpoints for GIS mapping of santri locations. This table is automatically populated/updated when santri scoring is calculated.

**Key Features:**
- ✅ Auto-updated when santri score is calculated or recalculated
- ✅ Returns GeoJSON format for map visualization
- ✅ Supports spatial queries (bounding box)
- ✅ Filter by poverty category or pesantren

### Get Santri GeoJSON
Get all santri as GeoJSON FeatureCollection for map display.

```
GET /api/santri-map/geojson?kategori=Miskin&pesantren_id={uuid}&limit=1000
```

**Query Parameters:**
- `kategori` (optional): Filter by kategori_kemiskinan (Sangat Miskin, Miskin, Rentan, Tidak Miskin)
- `pesantren_id` (optional, UUID): Filter by pesantren
- `limit` (default: 1000, max: 5000): Maximum records to return

**Response (200 OK):** GeoJSON FeatureCollection
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [108.123, -7.456]
      },
      "properties": {
        "id": "uuid",
        "santri_id": "uuid",
        "nama": "Ahmad Syarif",
        "skor_terakhir": 75,
        "kategori_kemiskinan": "Miskin",
        "pesantren_id": "uuid"
      }
    }
  ],
  "total": 150
}
```

**Frontend Implementation (Leaflet/Mapbox):**
```javascript
// Fetch santri locations
const response = await axios.get('/api/santri-map/geojson', {
  params: { kategori: 'Miskin', limit: 500 }
});

// Add to map (Leaflet example)
L.geoJSON(response.data, {
  pointToLayer: (feature, latlng) => {
    const props = feature.properties;
    return L.circleMarker(latlng, {
      radius: 8,
      fillColor: getColorByCategory(props.kategori_kemiskinan),
      color: '#fff',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    });
  },
  onEachFeature: (feature, layer) => {
    const props = feature.properties;
    layer.bindPopup(`
      <strong>${props.nama}</strong><br>
      Skor: ${props.skor_terakhir}<br>
      Kategori: ${props.kategori_kemiskinan}
    `);
  }
}).addTo(map);
```

### Get Santri by Bounding Box
Get santri within map viewport (bounding box) for optimized loading.

```
GET /api/santri-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2&kategori=Miskin
```

**Query Parameters:**
- `min_lon` (required): Minimum longitude
- `min_lat` (required): Minimum latitude
- `max_lon` (required): Maximum longitude
- `max_lat` (required): Maximum latitude
- `kategori` (optional): Filter by kategori_kemiskinan

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Found 25 santri",
  "data": [
    {
      "id": "uuid",
      "santri_id": "uuid",
      "nama": "Ahmad Syarif",
      "skor_terakhir": 75,
      "kategori_kemiskinan": "Miskin",
      "latitude": -7.456,
      "longitude": 108.123
    }
  ]
}
```

**Frontend Implementation (on map move):**
```javascript
map.on('moveend', async () => {
  const bounds = map.getBounds();
  const response = await axios.get('/api/santri-map/bbox', {
    params: {
      min_lon: bounds.getWest(),
      min_lat: bounds.getSouth(),
      max_lon: bounds.getEast(),
      max_lat: bounds.getNorth()
    }
  });
  
  // Update markers with visible santri only
  updateMarkers(response.data.data);
});
```

### Get Santri Map Statistics
Get statistics about santri map data.

```
GET /api/santri-map/statistics
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "total_santri": 500,
    "with_location": 450,
    "without_location": 50,
    "by_category": {
      "Sangat Miskin": 50,
      "Miskin": 120,
      "Rentan": 180,
      "Tidak Miskin": 100
    }
  }
}
```

---

## Pesantren Map GIS

**Purpose:** Specialized endpoints for GIS mapping of pesantren locations. This table is automatically populated/updated when pesantren scoring is calculated.

**Key Features:**
- ✅ Auto-updated when pesantren score is calculated or recalculated
- ✅ Returns GeoJSON format for map visualization
- ✅ Supports spatial queries (bounding box)
- ✅ Filter by quality category or region

### Get Pesantren GeoJSON
Get all pesantren as GeoJSON FeatureCollection for map display.

```
GET /api/pesantren-map/geojson?kategori=layak&provinsi=Jawa%20Barat&kabupaten=Tasikmalaya&limit=1000
```

**Query Parameters:**
- `kategori` (optional): Filter by kategori_kelayakan (sangat_layak, layak, cukup_layak, tidak_layak)
- `provinsi` (optional): Filter by provinsi
- `kabupaten` (optional): Filter by kabupaten
- `limit` (default: 1000, max: 5000): Maximum records to return

**Response (200 OK):** GeoJSON FeatureCollection
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [108.123, -7.456]
      },
      "properties": {
        "id": "uuid",
        "pesantren_id": "uuid",
        "nama": "Pondok Pesantren Al-Ikhlas",
        "nsp": "12345678",
        "skor_terakhir": 85,
        "kategori_kelayakan": "sangat_layak",
        "kabupaten": "Tasikmalaya",
        "provinsi": "Jawa Barat",
        "jumlah_santri": 500
      }
    }
  ],
  "total": 45
}
```

**Frontend Implementation (Leaflet/Mapbox):**
```javascript
// Fetch pesantren locations
const response = await axios.get('/api/pesantren-map/geojson', {
  params: { provinsi: 'Jawa Barat', limit: 100 }
});

// Add to map
L.geoJSON(response.data, {
  pointToLayer: (feature, latlng) => {
    const props = feature.properties;
    return L.marker(latlng, {
      icon: getPesantrenIcon(props.kategori_kelayakan)
    });
  },
  onEachFeature: (feature, layer) => {
    const props = feature.properties;
    layer.bindPopup(`
      <strong>${props.nama}</strong><br>
      NSP: ${props.nsp}<br>
      Skor: ${props.skor_terakhir}<br>
      Kategori: ${props.kategori_kelayakan}<br>
      Santri: ${props.jumlah_santri} orang<br>
      ${props.kabupaten}, ${props.provinsi}
    `);
  }
}).addTo(map);
```

### Get Pesantren by Bounding Box
Get pesantren within map viewport (bounding box) for optimized loading.

```
GET /api/pesantren-map/bbox?min_lon=106.8&min_lat=-6.3&max_lon=106.9&max_lat=-6.2&kategori=layak
```

**Query Parameters:**
- `min_lon` (required): Minimum longitude
- `min_lat` (required): Minimum latitude
- `max_lon` (required): Maximum longitude
- `max_lat` (required): Maximum latitude
- `kategori` (optional): Filter by kategori_kelayakan

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Found 12 pesantren",
  "data": [
    {
      "id": "uuid",
      "pesantren_id": "uuid",
      "nama": "Pondok Pesantren Al-Ikhlas",
      "nsp": "12345678",
      "skor_terakhir": 85,
      "kategori_kelayakan": "sangat_layak",
      "kabupaten": "Tasikmalaya",
      "provinsi": "Jawa Barat",
      "jumlah_santri": 500,
      "latitude": -7.456,
      "longitude": 108.123
    }
  ]
}
```

### Get Pesantren Map Statistics
Get statistics about pesantren map data.

```
GET /api/pesantren-map/statistics
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "total_pesantren": 150,
    "with_location": 145,
    "without_location": 5,
    "by_category": {
      "sangat_layak": 45,
      "layak": 60,
      "cukup_layak": 30,
      "tidak_layak": 10
    }
  }
}
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation description",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Data retrieved",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Common Status Codes
### Serialization Notes
- All responses use a standardized wrapper (`success`, `message`, `data`).
- Data is serialized using FastAPI's `jsonable_encoder` to ensure Pydantic models, `UUID`, and `datetime` values are JSON-safe.
- Nested relations (e.g., `pesantren`, `foto_santri`, `foto_pesantren`) are included where relevant.
- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Notes for Frontend Developers

1. **File Uploads**: 
   - Use `multipart/form-data` for endpoints with file uploads
   - Supported formats: jpg, jpeg, png, webp
   - Max file size: 5MB per file

2. **Date Format**: Use ISO 8601 format `YYYY-MM-DD`

3. **UUID**: All IDs are in UUID format (v4)

4. **Pagination**: Default page size is 20, max 100 items per page

5. **Authentication**: Include Bearer token in Authorization header for protected endpoints (if implemented)

6. **Scoring**: Automatically calculates based on available data. Missing data is handled gracefully with defaults.

7. **Enum Values**:
   - `jenis_kelamin`: "L", "P"
   - `status_tinggal`: "mondok", "pp", "mukim"
   - `jenis_aset`: "motor", "mobil", "sepeda", "hp", "laptop", "lahan", "ternak", "alat_kerja", "lainnya"
   - `sumber_biaya`: "orang_tua", "wali", "donatur", "beasiswa"
   - `status_pembayaran`: "lancar", "terlambat", "menunggak"
   - `status_gizi`: "baik", "kurang", "lebih"
   - `status_rumah`: "milik_sendiri", "kontrak", "menumpang"
   
8. **Pesantren Enum Values**:

   **Pesantren Pendidikan:**
   - `jenjang_pendidikan`: "semua_ra_ma", "pendidikan_dasar", "dasar_menengah_pertama", "dasar_menengah_atas", "satu_jenjang"
   - `kurikulum`: "terstandar", "internal", "tidak_jelas"
   - `akreditasi`: "a", "b", "c", "belum"
   - `prestasi_santri`: "nasional", "regional", "tidak_ada" (NOT "baik"!)

   **Pesantren Fasilitas:**
   - `asrama`: "layak", "cukup", "tidak_layak"
   - `ruang_belajar`: "layak", "cukup", "tidak_layak"
   - `internet`: "stabil", "tidak_stabil", "tidak_ada"
   - `fasilitas_transportasi`: "bus", "angkutan_umum", "kendaraan_pribadi", "ojek"
   - `akses_jalan`: "aspal", "cor_block", "tanah", "kerikil"

   **Pesantren Fisik:**
   - `status_bangunan`: "milik_sendiri", "sewa", "pinjam", "hibah", "wakaf"
   - `kondisi_bangunan`: "permanen", "semi_permanen", "non_permanen"
   - `sanitasi`: "layak", "cukup", "tidak_layak"
   - `air_bersih`: "lancar", "terbatas", "tidak_tersedia"
   - `sumber_air`: "sumur", "PDAM", "sungai", "hujan", "berbagai_macam"
   - `kualitas_air_bersih`: "asin", "layak_minum", "berbau", "keruh"
   - `fasilitas_mck`: "lengkap", "kurang_lengkap", "cukup", "tidak_layak"
   - `keamanan_bangunan`: "tinggi", "standar", "minim", "tidak_aman"
   - `jenis_lantai`: "keramik", "marmer", "kayu", "beton", "tanah"
   - `jenis_atap`: "genteng_tanah_liat", "metal", "seng", "upvc", "asbes", "ijuk"
   - `jenis_dinding`: "tembok", "kayu", "bambu", "anyaman", "papan"
   - `sumber_listrik`: "PLN", "genset", "listrik_tidak_ada", "tenaga_surya"
   - `daya_listrik_va`: "450", "900", "1300", "2200", "3500", "5500"
   - `kestabilan_listrik`: "stabil", "tidak_stabil", "tidak_ada"

9. **Pesantren Relationships**:
  - **Coordinates Extraction**: Both Santri detail and Pesantren detail expose `latitude` and `longitude` derived from geometry (POINT).
  - **Photos**: Santri and Pesantren return photo arrays; Pesantren also includes `foto_path` as the main photo.
  - **Static Uploads**: Serve images directly from `/uploads/...`; construct absolute URLs with the API base.
  - **GPS Recommendation**: When `status_tinggal = "mondok"`, clients should attempt to provide `latitude` and `longitude`. Backend accepts null, but coordinates improve map and GIS features.
   - All santri now have `pesantren_id` linking to their pesantren
   - Filter santri by pesantren: Add `?pesantren_id={uuid}` to any santri list endpoint
   - Each pesantren can have one fisik, fasilitas, and pendidikan record

---

**Last Updated:** December 28, 2025
