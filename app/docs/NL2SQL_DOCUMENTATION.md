# AI Query API Documentation

Sistem AI Query untuk mengkonversi pertanyaan pengguna dalam bahasa natural (Indonesia/Inggris) menjadi SQL queries yang aman dan dapat dieksekusi terhadap database.

## 📋 Daftar Isi

1. [Quick Start](#quick-start)
2. [Endpoints](#endpoints)
3. [Intent Types](#intent-types)
4. [Examples](#examples)
5. [Map Integration (Coordinates)](#map-integration-coordinates)
6. [Architecture](#architecture)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Deteksi Intent

Deteksi tipe intent dari query user:

```bash
curl -X POST "http://localhost:8000/nl2sql/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tunjukkan santri miskin di Bandung"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "filter",
    "confidence": 0.92,
    "keywords": ["tunjukkan", "miskin", "bandung"],
    "entity_types": ["santri", "kategori_kemiskinan", "lokasi"],
    "description": "User ingin filter santri dengan kondisi: miskin, lokasi: bandung"
  },
  "message": "Intent terdeteksi"
}
```

### 2. Jalankan AI Query

Konversi bahasa natural langsung ke SQL dan jalankan:

```bash
curl -X POST "http://localhost:8000/nl2sql/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tunjukkan 10 santri terbaru dengan skor tertinggi",
    "explain": true
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "ranking",
    "confidence": 0.88,
    "sql_query": "SELECT * FROM santri_pribadi ORDER BY created_at DESC LIMIT 10",
    "result": [
      {
        "id": "uuid-1",
        "nama_santri": "Ahmad Hidayat",
        "usia": 15,
        "kategori_kemiskinan": "Miskin",
        "skor": 75
      },
      ...
    ],
    "execution_time_ms": 145.5,
    "explanation": "Query terdeteksi intent: ranking. SQL melakukan query terhadap tabel: santri, skor"
  },
  "message": "Query berhasil dieksekusi"
}
```

### 3. List Available Intents

```bash
curl -X GET "http://localhost:8000/nl2sql/intents"
```

---

## Endpoints

### POST `/nl2sql/detect-intent`

Deteksi intent dari natural language query tanpa menjalankan SQL.

**Request:**
```json
{
  "query": "string - pertanyaan user dalam bahasa natural"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "string - tipe intent (LIST, FILTER, COUNT, dll)",
    "confidence": 0.0-1.0,
    "keywords": ["string"],
    "entity_types": ["string"],
    "description": "string - penjelasan human-readable"
  }
}
```

**Status Codes:**
- `200` - Intent berhasil terdeteksi
- `400` - Query invalid atau empty
- `500` - Internal server error

---

### POST `/nl2sql/query`

Jalankan NL2SQL query lengkap (intent detection → SQL generation → execution).

**Request:**
```json
{
  "query": "string - pertanyaan user",
  "explain": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": "string",
    "confidence": 0.0-1.0,
    "sql_query": "string - SQL yang dihasilkan",
    "result": [object] atau [array] - hasil query,
    "execution_time_ms": 123.45,
    "explanation": "string - optional, hanya jika explain=true"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "string - deskripsi error",
  "status_code": 400
}
```

**Status Codes:**
- `200` - Query berhasil dieksekusi
- `400` - Query invalid atau SQL validation failed
- `500` - OpenAI API error atau database error

---

### GET `/nl2sql/intents`

List semua tipe intent yang tersedia dengan deskripsi dan contoh.

**Response:**
```json
{
  "success": true,
  "data": {
    "intents": [
      {
        "type": "list",
        "description": "Ambil data santri, pesantren, dll",
        "examples": [
          "Tunjukkan semua santri",
          "Lihat list pesantren"
        ]
      },
      ...
    ]
  }
}
```

---

### POST `/nl2sql/test`

Test NL2SQL system dengan predefined test queries.

**Response:**
```json
{
  "success": true,
  "data": {
    "test_results": [
      {
        "query": "Tunjukkan 10 santri terbaru",
        "intent": "list",
        "success": true,
        "error": null
      },
      ...
    ]
  }
}
```

---

## Intent Types

| Intent | Deskripsi | Contoh |
|--------|-----------|---------|
| **LIST** | Ambil data lengkap | "Tunjukkan semua santri", "Lihat list pesantren" |
| **FILTER** | Filter berdasarkan kondisi | "Santri miskin di Bandung", "Pesantren berkategori layak" |
| **COUNT** | Hitung jumlah | "Berapa santri?", "Ada berapa pesantren di Jawa Barat?" |
| **STATISTICS** | Statistik/agregasi | "Rata-rata skor santri", "Distribusi kategori kemiskinan" |
| **TREND** | Analisis trend/perubahan | "Trend santri miskin tahun ini", "Peningkatan skor pesantren" |
| **RANKING** | Sorting/ranking | "Top 10 santri terbaik", "Pesantren terburuk", "Ranking skor" |
| **LOCATION** | Query berbasis lokasi | "Peta santri", "Lokasi pesantren di Bandung", "Koordinat santri" |
| **DISTANCE** | Query radius/jarak | "Santri dalam 10km radius", "Pesantren terdekat", "Jarak dengan pesantren" |
| **HEATMAP** | Visualisasi density | "Heatmap kemiskinan santri", "Distribusi spasial pesantren" |
| **SCORING** | Query tentang score | "Skor santri Ahmad", "Kelayakan pesantren", "Penilaian kategori" |
| **CATEGORY** | Query kategori/klasifikasi | "Santri kategori sangat miskin", "Pesantren berkategori sangat layak" |
| **HELP** | Bantuan/informasi | "Bagaimana cara...?", "Apa itu santri?", "Jelaskan..." |
| **UNKNOWN** | Tidak terdeteksi | Query yang tidak sesuai dengan intent lainnya |

---

## Examples

### Contoh 1: LIST Intent

**Query:**
```
"Tunjukkan 10 santri terbaru"
```

**Intent Detection:**
- Intent: `LIST`
- Confidence: `0.95`
- Entity Types: `santri`

**Generated SQL:**
```sql
SELECT * FROM santri_pribadi 
ORDER BY created_at DESC 
LIMIT 10
```

### Contoh 2: FILTER Intent

**Query:**
```
"Santri miskin di Jawa Barat"
```

**Intent Detection:**
- Intent: `FILTER`
- Confidence: `0.92`
- Entity Types: `santri`, `kategori_kemiskinan`, `lokasi`

**Generated SQL:**
```sql
SELECT s.* FROM santri_pribadi s
WHERE s.kategori_kemiskinan = 'Miskin'
AND s.provinsi = 'Jawa Barat'
LIMIT 1000
```

### Contoh 3: COUNT Intent

**Query:**
```
"Berapa jumlah santri miskin di Bandung?"
```

**Intent Detection:**
- Intent: `COUNT`
- Confidence: `0.88`
- Entity Types: `santri`, `kategori_kemiskinan`, `lokasi`

**Generated SQL:**
```sql
SELECT COUNT(*) as total FROM santri_pribadi
WHERE kategori_kemiskinan = 'Miskin'
AND kota = 'Bandung'
```

### Contoh 4: RANKING Intent

**Query:**
```
"Top 5 pesantren dengan skor tertinggi di Jawa Barat"
```

**Intent Detection:**
- Intent: `RANKING`
- Confidence: `0.91`
- Entity Types: `pesantren`, `score`, `lokasi`

**Generated SQL:**
```sql
SELECT p.*, ps.skor_keseluruhan FROM pondok_pesantren p
LEFT JOIN pesantren_skor ps ON p.id = ps.pesantren_id
WHERE p.provinsi = 'Jawa Barat'
ORDER BY ps.skor_keseluruhan DESC
LIMIT 5
```

### Contoh 5: LOCATION/HEATMAP Intent

**Query:**
```
"Peta distribusi santri kemiskinan"
```

**Intent Detection:**
- Intent: `LOCATION` atau `HEATMAP`
- Entity Types: `santri`, `kategori_kemiskinan`, `lokasi`

**Generated SQL:**
```sql
SELECT s.*, sm.latitude, sm.longitude, s.kategori_kemiskinan
FROM santri_pribadi s
LEFT JOIN santri_map sm ON s.id = sm.santri_id
WHERE sm.latitude IS NOT NULL AND sm.longitude IS NOT NULL
LIMIT 1000
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Layer                         │
│  POST /nl2sql/detect-intent, /nl2sql/query, etc.            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 NL2SQL Routes Layer                          │
│              (app/routes/nl2sql_routes.py)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   NL2SQL Service Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ NL2SQLService.process_query()                        │  │
│  │  ├─ classify_intent()     [Intent Classifier]        │  │
│  │  ├─ generate_sql()        [OpenAI ChatGPT]           │  │
│  │  ├─ validate_sql()        [Safety Checker]           │  │
│  │  └─ execute_sql()         [SQLAlchemy]               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
     ↓                   ↓                   ↓
┌─────────────┐  ┌──────────────────┐  ┌─────────────┐
│   Intent    │  │   OpenAI API     │  │  PostgreSQL │
│ Classifier  │  │  (ChatGPT model) │  │  Database   │
└─────────────┘  └──────────────────┘  └─────────────┘
```

### Processing Pipeline

```
1. User Query (Natural Language)
   ↓
2. Intent Classifier
   - Keyword matching (keyword→intent score)
   - Entity detection (tabel/field apa yang relevan)
   - Confidence scoring
   ↓
3. Schema Context Loading
   - Load schema_context.json (database structure)
   - Format untuk OpenAI context window
   ↓
4. SQL Generation (OpenAI ChatGPT)
   - System prompt: "Generate safe SELECT SQL..."
   - User message: Query + detected intent + schema
   - Model: gpt-4-turbo
   - Temperature: 0.3 (consistent results)
   ↓
5. SQL Validation
   - Check: Must be SELECT only
   - Check: No dangerous keywords (DROP, DELETE, UPDATE)
   - Check: Must have LIMIT clause
   - Check: LIMIT value ≤ 1000
   ↓
6. SQL Execution
   - Execute via SQLAlchemy text()
   - Parameterized queries (safe)
   - Row-to-dict conversion
   ↓
7. Response Assembly
   - Return: intent, sql_query, result, execution_time, error
```

### File Structure

```
app/nl2sql/
├── intent_classifier.py      # Intent detection (keyword-based)
├── nl2sql_service.py         # Main service (orchestrator)
├── schema_context.json       # Database schema for GPT context
└── ...

app/routes/
├── nl2sql_routes.py          # FastAPI endpoints
└── ...

app/core/
└── config.py                 # OpenAI configuration

app/
└── main.py                   # Register nl2sql_router
```

---

## Map Integration (Coordinates)

### 🗺️ Overview

NL2SQL queries otomatis menambahkan koordinat (latitude/longitude) untuk hasil yang dapat ditampilkan di peta interaktif. Fitur ini memungkinkan visualisasi data santri dan pesantren di peta.

### Coordinate Support

#### Santri Queries

Semua query santri (non-agregasi) otomatis menambahkan `latitude` dan `longitude` dari tabel `santri_pribadi`:

**Example Query:**
```
"Berikan 10 santri dengan skor tertinggi"
```

**Generated SQL:**
```sql
SELECT sp.id, sp.nama, sp.latitude, sp.longitude, ss.skor_total
FROM santri_pribadi sp
JOIN santri_skor ss ON sp.id = ss.santri_id
ORDER BY ss.skor_total DESC
LIMIT 10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "result": [
      {
        "id": "uuid-1",
        "nama": "Ahmad Hidayat",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "skor_total": 92
      },
      {
        "id": "uuid-2", 
        "nama": "Siti Nurhaliza",
        "latitude": -6.1944,
        "longitude": 107.0091,
        "skor_total": 88
      }
    ]
  }
}
```

#### Pesantren Queries

Semua query pesantren (non-agregasi) otomatis mengekstrak koordinat dari PostGIS geometry field di tabel `pesantren_map`:

**Example Query:**
```
"Pesantren dengan skor tertinggi di Jawa Barat"
```

**Generated SQL:**
```sql
SELECT pp.id, pp.nama, ps.skor_total, 
       ST_Y(pm.lokasi::geometry) as latitude,
       ST_X(pm.lokasi::geometry) as longitude
FROM pondok_pesantren pp
JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
JOIN pesantren_map pm ON pp.id = pm.pesantren_id
WHERE pp.provinsi = 'Jawa Barat'
ORDER BY ps.skor_total DESC
LIMIT 50
```

**Response:**
```json
{
  "success": true,
  "data": {
    "result": [
      {
        "id": "uuid-1",
        "nama": "Pondok Pesantren Al-Muhtadin",
        "skor_total": 95,
        "latitude": -7.0562,
        "longitude": 107.7564
      },
      {
        "id": "uuid-2",
        "nama": "Pondok Pesantren Al-Azhar",
        "skor_total": 89,
        "latitude": -6.3111,
        "longitude": 107.0298
      }
    ]
  }
}
```

### Usage in Frontend

Gunakan koordinat untuk menampilkan marker di peta interaktif (menggunakan Leaflet, Mapbox, atau Google Maps):

```javascript
// Assuming response dari /nl2sql/query endpoint
const response = await fetch('/nl2sql/query', {
  method: 'POST',
  body: JSON.stringify({ query: "Pesantren di Jawa Barat" })
});

const data = await response.json();

// Create map markers
data.data.result.forEach(item => {
  const marker = L.marker(
    [item.latitude, item.longitude],
    {
      title: item.nama,
      popup: `${item.nama} - Skor: ${item.skor_total}`
    }
  ).addTo(map);
});
```

### Coordinate Extraction Methods

#### PostGIS ST_X() dan ST_Y()

Untuk pesantren, koordinat diambil dari geometry field menggunakan PostGIS functions:

```sql
-- Extract longitude (X coordinate)
ST_X(pm.lokasi::geometry) as longitude

-- Extract latitude (Y coordinate)  
ST_Y(pm.lokasi::geometry) as latitude
```

#### Direct Columns (Santri)

Untuk santri, koordinat langsung dari kolom tabel:

```sql
SELECT sp.latitude, sp.longitude
FROM santri_pribadi sp
```

### Important Notes

⚠️ **Aggregate Queries (GROUP BY) tidak include koordinat**

Ketika query menggunakan `GROUP BY` (agregasi per wilayah), koordinat tidak disertakan:

```
"Berapa jumlah pesantren per kabupaten di Jawa Barat"
```

**Response (tanpa latitude/longitude):**
```json
{
  "result": [
    { "kabupaten": "Bandung", "jumlah_pesantren": 45 },
    { "kabupaten": "Bogor", "jumlah_pesantren": 32 }
  ]
}
```

Ini adalah perilaku yang benar karena agregasi tidak memiliki single latitude/longitude.

---

### Safety Measures

#### 1. SQL Validation
```python
# Only SELECT queries allowed
if "SELECT" not in sql.upper():
    raise ValueError("Only SELECT queries allowed")

# No dangerous keywords
dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
if any(keyword in sql.upper() for keyword in dangerous):
    raise ValueError("Query contains dangerous keywords")

# Must have LIMIT
if "LIMIT" not in sql.upper():
    raise ValueError("Query must include LIMIT clause")

# LIMIT value check
if limit_value > 1000:
    raise ValueError("LIMIT must be <= 1000")
```

#### 2. Parameterized Queries
```python
# Using SQLAlchemy text() with parameters
from sqlalchemy import text

stmt = text("SELECT * FROM santri WHERE id = :id LIMIT :limit")
result = db.execute(stmt, {"id": user_id, "limit": 10})
```

#### 3. API Key Security
```python
# Never hardcode API keys
# Use .env file with secrets
OPENAI_API_KEY=sk-...  # Loaded via pydantic-settings

# .env never committed to git
# See .gitignore: .env
```

#### 4. Rate Limiting (Recommended)
```python
# Add to FastAPI endpoints:
from fastapi_limiter import FastAPILimiter

@limiter.limit("10/minute")
def nl2sql_query(request: NL2SQLRequest):
    ...
```

#### 5. Query Logging
```python
# Log all user queries for audit trail
import logging
logger = logging.getLogger("nl2sql")
logger.info(f"User query: {query}")
logger.info(f"Generated SQL: {sql}")
logger.info(f"Result count: {len(result)}")
```

### Best Practices

1. **Never trust user input directly** - Always validate and sanitize
2. **Use parameterized queries** - Prevents SQL injection
3. **Limit query results** - LIMIT clause required
4. **Log everything** - For debugging and audit
5. **Monitor OpenAI costs** - Set usage limits
6. **Test with edge cases** - Injection attempts, malformed queries

---

## Troubleshooting

### Error: "OpenAI API Key not found"

**Problem:** OPENAI_API_KEY tidak diset

**Solution:**
```bash
# 1. Set environment variable
export OPENAI_API_KEY="sk-your-key-here"

# 2. Atau set di .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# 3. Verifikasi
python -c "from app.core.config import settings; print(settings.OPENAI_API_KEY)"
```

### Error: "Query must include LIMIT clause"

**Problem:** Generated SQL tidak memiliki LIMIT

**Solution:**
```python
# Coba query yang lebih spesifik
"Tunjukkan 10 santri pertama"  # Instead of "Tunjukkan semua santri"
"Top 5 pesantren"             # Instead of "Pesantren mana saja"
```

### Error: "LIMIT value must be <= 1000"

**Problem:** Query hasil terlalu banyak record

**Solution:**
```python
# Modifikasi query
"Tunjukkan 100 santri terbaru"     # Instead of 5000
"Top 50 pesantren dengan skor tertinggi"  # Instead of 2000
```

### Error: "Invalid SQL generated"

**Problem:** OpenAI menghasilkan SQL yang tidak valid

**Solution:**
```python
# 1. Gunakan query yang lebih jelas
"Santri dengan skor lebih dari 75" 
# Instead of "Santri bagus"

# 2. Spesifikkan field yang ingin ditampilkan
"Tunjukkan nama dan skor santri"
# Instead of "Tunjukkan data santri"

# 3. Check actual table names di /nl2sql/intents
# Verify schema di app/nl2sql/schema_context.json
```

### Error: "OpenAI API rate limited"

**Problem:** Terlalu banyak request ke OpenAI

**Solution:**
```python
# 1. Implement caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cache_sql_result(query: str):
    ...

# 2. Add backoff strategy
import time
for attempt in range(3):
    try:
        result = service.process_query(query)
        break
    except RateLimitError:
        time.sleep(2 ** attempt)  # Exponential backoff

# 3. Monitor usage di https://platform.openai.com/account/usage
```

### Performance Slow

**Problem:** NL2SQL queries lambat

**Solution:**
```python
# 1. Check database indexes
# Create indexes untuk frequently queried fields
CREATE INDEX idx_santri_kategori ON santri_pribadi(kategori_kemiskinan);
CREATE INDEX idx_santri_provinsi ON santri_pribadi(provinsi);

# 2. Add EXPLAIN to see query plan
EXPLAIN ANALYZE SELECT ... FROM ...

# 3. Reduce result limit
# Encourage "Top 10" instead of "All"

# 4. Monitor execution_time_ms in response
# If > 500ms, optimize the database query
```

---

## Next Steps

1. **Test the endpoints** - Use `/nl2sql/test` endpoint
2. **Monitor OpenAI costs** - Check usage dashboard
3. **Implement caching** - For common queries
4. **Add authentication** - Protect endpoints with API keys
5. **Create client SDK** - For frontend integration
6. **Setup logging/monitoring** - Sentry, LogRocket, etc.

---

## Reference

- OpenAI API Docs: https://platform.openai.com/docs/api-reference
- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- Intent Types Reference: `/nl2sql/intents` endpoint
- Schema Documentation: `app/nl2sql/schema_context.json`
