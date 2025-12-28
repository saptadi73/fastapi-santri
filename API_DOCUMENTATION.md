# API Documentation - FastAPI Santri

**Base URL:** `http://localhost:8000`

---

## Table of Contents
1. [Authentication](#authentication)
2. [Photo Management](#photo-management-overview)
3. [GIS / Map Endpoints](#gis--map-endpoints)
4. [Santri Pribadi (Core Data)](#santri-pribadi-core-data)
5. [Santri Orangtua (Parents)](#santri-orangtua-parents)
6. [Santri Rumah (House)](#santri-rumah-house)
7. [Santri Asset (Aset)](#santri-asset-aset)
8. [Santri Bansos (Bantuan Sosial)](#santri-bansos-bantuan-sosial)
9. [Santri Kesehatan (Health)](#santri-kesehatan-health)
10. [Santri Pembiayaan (Financing)](#santri-pembiayaan-financing)
11. [Scoring System](#scoring-system)
12. [Pondok Pesantren (Main Data)](#pondok-pesantren-main-data)
13. [Pesantren Fisik (Physical Infrastructure)](#pesantren-fisik-physical-infrastructure)
14. [Pesantren Fasilitas (Facilities)](#pesantren-fasilitas-facilities)
15. [Pesantren Pendidikan (Education)](#pesantren-pendidikan-education)
16. [Pesantren Scoring System](#pesantren-scoring-system)
17. [Response Format](#response-format)

---

## Photo Management Overview

Photo management is available for three main entities:
- **Santri Pribadi** (foto_santri) - Student photos
- **Santri Orangtua** (foto_orangtua) - Parent/Guardian photos  
- **Santri Asset** (foto_asset) - Asset/Property photos

### General Photo Endpoints Pattern

For each entity, three photo operations are available:

**Add Photos:**
```
POST /api/{entity}/{entity_id}/photos
```

**Update Photo:**
```
PUT /api/{entity}/photos/{foto_id}
```

**Delete Photo:**
```
DELETE /api/{entity}/photos/{foto_id}
```

Where `{entity}` is one of: `santri-pribadi`, `santri-orangtua`, `santri-asset`

### File Upload Requirements
- **Supported Formats:** jpg, jpeg, png, webp
- **Max Size per File:** 5MB
- **Multiple Files:** Yes, allowed in add/create operations

### Photo Response Format
All photo endpoints return consistent structure:
```json
{
  "id": "UUID",
  "santri_id": "UUID" | "orangtua_id": "UUID" | "asset_id": "UUID",
  "nama_file": "filename.jpg",
  "url_photo": "/uploads/entity/filename.jpg"
}
```

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
    "pondok": {
      "id": "660e8400-e29b-41d4-a716-446655440099",
      "nama": "Pondok Pesantren Al-Ikhlas"
    },
    "provinsi": "Jawa Barat",
    "kabupaten": "Bandung",
    "kecamatan": "Bandung Kota",
    "desa": "Desa Maju",
    "foto_santri": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "nama_file": "ahmad_1.jpg",
        "url": "/uploads/santri/ahmad_1.jpg"
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
      "foto_count": 1
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "nama": "Nur Azizah",
      "hubungan": "ibu",
      "pekerjaan": "Ibu Rumah Tangga",
      "status_hidup": "hidup",
      "foto_count": 1
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
      "daya_listrik_va": "2200"
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
Retrieve full details of a house record.

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
    "daya_listrik_va": "2200"
  }
}
```

### Get Rumah by Santri
Retrieve house information for a specific santri.

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
    "daya_listrik_va": "2200"
  }
}
```

### Create New Rumah
Create a new house record for a santri.

```
POST /api/santri-rumah
Content-Type: application/json
```

**Request Body:**
```json
{
  "santri_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_rumah": "milik_sendiri",
  "jenis_lantai": "keramik",
  "jenis_dinding": "tembok",
  "jenis_atap": "genteng",
  "akses_air_bersih": "layak",
  "daya_listrik_va": "2200"
}
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
    "daya_listrik_va": "2200"
  }
}
```

### Update Rumah
Update house data (partial update).

```
PUT /api/santri-rumah/{rumah_id}
Content-Type: application/json
```

**Request Body:** (all optional)
```json
{
  "status_rumah": "kontrak",
  "jenis_lantai": "semen",
  "daya_listrik_va": "1300"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data rumah berhasil diupdate",
  "data": { ... }
}
```

### Delete Rumah
Delete a house record.

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
  "message": "Data aset berhasil diambil",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "jenis_aset": "motor",
      "jumlah": 1,
      "nilai_perkiraan": 15000000
    }
  ],
  "pagination": { ... }
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
  "message": "Detail aset berhasil diambil",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "santri_id": "550e8400-e29b-41d4-a716-446655440000",
    "jenis_aset": "motor",
    "jumlah": 1,
    "nilai_perkiraan": 15000000
  }
}
```

### Get Assets by Santri
```
GET /api/santri-asset/santri/{santri_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data aset berhasil diambil",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "jenis_aset": "motor",
      "jumlah": 1,
      "nilai_perkiraan": 15000000
    }
  ]
}
```

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
  "message": "Data aset berhasil ditambahkan",
  "data": { ... }
}
```

### Update Asset
```
PUT /api/santri-asset/{asset_id}
Content-Type: application/json
```

**Request Body:** (all optional)
```json
{
  "jenis_aset": "mobil",
  "jumlah": 2,
  "nilai_perkiraan": 50000000
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data aset berhasil diupdate",
  "data": { ... }
}
```

### Delete Asset
```
DELETE /api/santri-asset/{asset_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data aset berhasil dihapus",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002"
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
  "message": "2 foto berhasil ditambahkan",
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
  "message": "Foto berhasil diupdate",
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
  "message": "Foto berhasil dihapus",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440004"
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
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "santri_id": "550e8400-e29b-41d4-a716-446655440000",
      "tinggi_badan": 165.5,
      "berat_badan": 55.0,
      "status_gizi": "baik",
      "riwayat_penyakit": "Demam tinggi",
      "alergi_obat": "Amoksisilin",
      "kebutuhan_khusus": null
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
  "santri_id": "550e8400-e29b-41d4-a716-446655440000",
  "tinggi_badan": 165.5,
  "berat_badan": 55.0,
  "status_gizi": "baik",
  "riwayat_penyakit": "Demam tinggi",
  "alergi_obat": "Amoksisilin",
  "kebutuhan_khusus": null
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Data kesehatan berhasil ditambahkan",
  "data": { ... }
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
  "berat_badan": 56.5,
  "status_gizi": "baik",
  "riwayat_penyakit": "Demam tinggi, perlu pemeriksaan lanjut"
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

### Calculate Single Santri Score
Calculate poverty score for a single santri based on `scoring.json` config.

```
POST /api/scoring/{santri_id}/calculate
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Skor berhasil dihitung dan disimpan",
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
    "calculated_at": "2025-12-28T10:30:45.123Z"
  }
}
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

### Get Score by Santri ID
Retrieve latest score for a santri.

```
GET /api/scoring/santri/{santri_id}
```

**Path Parameters:**
- `santri_id` (UUID): Santri ID

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
| Ekonomi | 30% | 40 | penghasilan_bulanan, jumlah_tanggungan, status_pekerjaan |
| Rumah | 25% | 43 | status_kepemilikan, luas_per_orang, lantai, sanitasi |
| Aset | 15% | 23 | motor, mobil, lahan |
| Pembiayaan | 15% | 25 | sumber_biaya, tunggakan |
| Kesehatan | 10% | 25 | penyakit_kronis, bpjs_aktif |
| Bansos | 5% | 17 | pernah_menerima, dtks |

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
  "lokasi": {
    "type": "Point",
    "coordinates": [108.123, -7.456]
  },
  "telepon": "081234567890",
  "email": "info@pesantren.com",
  "website": "www.pesantren.com",
  "nama_kyai": "KH. Ahmad",
  "jumlah_santri": 500,
  "jumlah_guru": 25,
  "tahun_berdiri": 1985,
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

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
  "status_bangunan": "milik_sendiri",
  "kondisi_bangunan": "permanen",
  "sumber_air": "PDAM",
  "kualitas_air_bersih": "layak_minum",
  "fasilitas_mck": "lengkap",
  "jumlah_mck": 20,
  "jenis_lantai": "keramik",
  "jenis_dinding": "tembok",
  "jenis_atap": "genteng_tanah_liat",
  "sumber_listrik": "PLN",
  "daya_listrik_va": "5500",
  "kestabilan_listrik": "stabil",
  "sistem_keamanan": "ada"
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
  "status_bangunan": "milik_sendiri",
  "kondisi_bangunan": "permanen",
  "sumber_air": "PDAM",
  "kualitas_air_bersih": "layak_minum",
  "fasilitas_mck": "lengkap",
  "jumlah_mck": 20,
  "jenis_lantai": "keramik",
  "jenis_dinding": "tembok",
  "jenis_atap": "genteng_tanah_liat",
  "sumber_listrik": "PLN",
  "daya_listrik_va": "5500",
  "kestabilan_listrik": "stabil",
  "sistem_keamanan": "ada"
}
```

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
  "fasilitas_olahraga": "lapangan_futsal,basket",
  "fasilitas_kesehatan": "klinik",
  "koperasi": true,
  "kantin": true,
  "fasilitas_mengajar": "projector,whiteboard",
  "fasilitas_komunikasi": "internet,telepon",
  "akses_transportasi": "angkutan_umum",
  "akses_jalan": "aspal",
  "jarak_ke_kota_km": 5.5
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

**Request Body:** Same as response above (all fields optional except pesantren_id)

**Response (201 Created):** Same as detail response

**Note:** Only one fasilitas record per pesantren is allowed.

### Update Fasilitas Data
```
PUT /pesantren-fasilitas/{fasilitas_id}
```

**Request Body:** Same as create (all fields optional)

**Response (200 OK):** Same as detail response

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
  "jenjang_pendidikan": "SD,SMP,SMA",
  "kurikulum": "terstandar",
  "akreditasi": "A",
  "jumlah_guru_tetap": 20,
  "jumlah_guru_tidak_tetap": 5,
  "guru_s1_keatas": 18,
  "prestasi_akademik": "nasional",
  "prestasi_non_akademik": "regional",
  "program_unggulan": "Tahfidz,Bahasa Arab",
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

**Request Body:** Same as response above (all fields optional except pesantren_id)

**Response (201 Created):** Same as detail response

**Note:** Only one pendidikan record per pesantren is allowed.

### Update Pendidikan Data
```
PUT /pesantren-pendidikan/{pendidikan_id}
```

**Request Body:** Same as create (all fields optional)

**Response (200 OK):** Same as detail response

### Delete Pendidikan Data
```
DELETE /pesantren-pendidikan/{pendidikan_id}
```

**Response (204 No Content)**

---

## Pesantren Scoring System

### Calculate Pesantren Score
Calculate and save quality score for a pesantren.

```
POST /api/pesantren-scoring/{pesantren_id}/calculate
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "pesantren_id": "uuid",
  "skor_kelayakan_fisik": 85,
  "skor_air_sanitasi": 90,
  "skor_fasilitas_pendukung": 75,
  "skor_mutu_pendidikan": 80,
  "skor_total": 83,
  "kategori_kelayakan": "sangat_layak",
  "metode": "weighted_average",
  "version": "1.0",
  "calculated_at": "2025-12-28T10:30:00"
}
```

**Scoring Dimensions:**
- **Kelayakan Fisik (40%)**: Status bangunan, kondisi, luas
- **Air & Sanitasi (25%)**: Sumber air, kualitas, MCK
- **Fasilitas Pendukung (20%)**: Ruang kelas, perpustakaan, olahraga
- **Mutu Pendidikan (15%)**: Akreditasi, guru, prestasi

**Kategori Kelayakan:**
- `sangat_layak`: Skor 80-100 (Excellent condition)
- `layak`: Skor 60-79 (Good condition)
- `cukup_layak`: Skor 40-59 (Fair condition)
- `tidak_layak`: Skor 0-39 (Poor condition)

### Get Score by Pesantren ID
```
GET /api/pesantren-scoring/pesantren/{pesantren_id}
```

**Response (200 OK):** Same as calculate response

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
   - `status_bangunan`: "milik_sendiri", "sewa", "pinjam", "hibah", "wakaf"
   - `kondisi_bangunan`: "permanen", "semi_permanen", "non_permanen"
   - `sumber_air`: "sumur", "PDAM", "sungai", "hujan", "berbagai_macam"
   - `kualitas_air_bersih`: "asin", "layak_minum", "berbau", "keruh"
   - `fasilitas_mck`: "lengkap", "kurang_lengkap", "cukup", "tidak_layak"
   - `kestabilan_listrik`: "stabil", "tidak_stabil", "tidak_ada"
   - `jenis_lantai`: "keramik", "marmer", "kayu", "beton", "tanah"
   - `jenis_atap`: "genteng_tanah_liat", "metal", "seng", "upvc", "asbes", "ijuk"
   - `jenis_dinding`: "tembok", "kayu", "bambu", "anyaman", "papan"
   - `sumber_listrik`: "PLN", "genset", "listrik_tidak_ada", "tenaga_surya"
   - `kurikulum`: "terstandar", "internal", "tidak_jelas"
   - `akreditasi`: "A", "B", "C", "belum"
   - `prestasi_akademik/non_akademik`: "nasional", "regional", "tidak_ada"
   - `metode_pembayaran`: "tunai", "non_tunai", "campuran"
   - `akses_jalan`: "aspal", "cor_block", "tanah", "kerikil"

9. **Pesantren Relationships**:
   - All santri now have `pesantren_id` linking to their pesantren
   - Filter santri by pesantren: Add `?pesantren_id={uuid}` to any santri list endpoint
   - Each pesantren can have one fisik, fasilitas, and pendidikan record

---

**Last Updated:** December 28, 2025
