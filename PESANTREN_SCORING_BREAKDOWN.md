# Pesantren Scoring Breakdown

## Overview
Sistem scoring pesantren sekarang dilengkapi dengan breakdown detail yang komprehensif, mirip dengan santri scoring. Breakdown ini memberikan transparansi penuh tentang bagaimana skor dihitung dan dari mana nilainya berasal.

## Struktur Breakdown

### Response Format
```json
{
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
    "version": "1.1"
  },
  "breakdown": {
    "dimensi": [...],
    "skor_total": 94,
    "kategori_kelayakan": "sangat_layak",
    "interpretasi_kategori": "Kondisi sangat baik, memenuhi semua standar kelayakan"
  }
}
```

### Breakdown Dimensi
Setiap dimensi dalam breakdown memiliki struktur:
```json
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
    ...
  ]
}
```

## Dimensi Scoring

### 1. Kelayakan Fisik Bangunan (40%)
Parameter yang dinilai:
- **Kondisi Bangunan**: permanen (100), semi_permanen (70), non_permanen (40)
- **Status Bangunan**: milik_sendiri (100), wakaf (95), hibah (85), pinjam (65), sewa (60)
- **Keamanan Bangunan**: tinggi (100), standar (80), minim (60), tidak_aman (30)
- **Jenis Lantai**: marmer (100), keramik (90), beton (70), kayu (65), tanah (30)
- **Jenis Dinding**: tembok (100), papan (70), kayu (65), bambu (50), anyaman (40)
- **Jenis Atap**: genteng_tanah_liat (100), metal (90), upvc (85), seng (60), asbes (50), ijuk (40)

### 2. Air Bersih dan Sanitasi (25%)
Parameter yang dinilai:
- **Air Bersih**: lancar (100), terbatas (60), tidak_tersedia (20)
- **Sumber Air**: PDAM (100), sumur (80), berbagai_macam (75), hujan (50), sungai (30)
- **Kualitas Air**: layak_minum (100), keruh (60), berbau (40), asin (30)
- **Sanitasi**: layak (100), cukup (70), tidak_layak (30)

### 3. Fasilitas Pendukung (20%)
Parameter yang dinilai:
- **Sumber Listrik**: PLN (100), tenaga_surya (85), genset (60), listrik_tidak_ada (20)
- **Kestabilan Listrik**: stabil (100), tidak_stabil (60), tidak_ada (20)
- **Fasilitas Mengajar**: projector (100), tv_monitor (85), whiteboard (80), papan_tulis (70)
- **Fasilitas Komunikasi**: internet (100), telepon (70), pos (50)
- **Fasilitas Transportasi**: bus (100), angkutan_umum (80), kendaraan_pribadi (70), ojek (60)
- **Akses Jalan**: aspal (100), cor_block (85), kerikil (60), tanah (40)

### 4. Mutu Pendidikan (15%)
Parameter yang dinilai:
- **Jenjang Pendidikan**: semua_ra_ma (100), dasar_menengah_atas (90), dasar_menengah_pertama (75), pendidikan_dasar (60), satu_jenjang (50)
- **Kurikulum**: terstandar (100), internal (75), tidak_jelas (40)
- **Akreditasi**: a (100), b (80), c (60), belum (40)
- **Prestasi Santri**: nasional (100), regional (75), tidak_ada (40)

## Kategori Kelayakan

| Skor Total | Kategori | Interpretasi |
|-----------|----------|--------------|
| ≥ 85 | sangat_layak | Kondisi sangat baik, memenuhi semua standar kelayakan |
| 70-84 | layak | Kondisi baik, memenuhi standar kelayakan |
| 55-69 | cukup_layak | Kondisi cukup, perlu perbaikan di beberapa aspek |
| < 55 | tidak_layak | Kondisi kurang baik, memerlukan perbaikan menyeluruh |

## Interpretasi Skor Dimensi

Setiap dimensi memiliki interpretasi berdasarkan skornya:
- **≥ 85**: Sangat Baik
- **70-84**: Baik
- **55-69**: Cukup
- **< 55**: Kurang

## API Endpoints

### 1. Calculate Scoring
```http
POST /api/pesantren-scoring/{pesantren_id}/calculate
```
**Response:**
```json
{
  "success": true,
  "message": "Skor pesantren berhasil dihitung dan disimpan",
  "data": {
    "skor": { ... },
    "breakdown": { ... }
  }
}
```

### 2. Get Scoring by Pesantren ID
```http
GET /api/pesantren-scoring/pesantren/{pesantren_id}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "skor": { ... },
    "breakdown": { ... }
  }
}
```

### 3. Batch Calculate All
```http
POST /api/pesantren-scoring/batch/calculate-all
```
Menghitung scoring untuk semua pesantren dalam database.

## Contoh Penggunaan

### Python/Script
```python
from app.services.pesantren_score_service import PesantrenScoreService
from app.core.database import SessionLocal

with SessionLocal() as db:
    svc = PesantrenScoreService(db)
    record, breakdown = svc.calculate_and_save(pesantren_id)
    
    # Akses hasil scoring
    print(f"Total: {record.skor_total}")
    print(f"Kategori: {record.kategori_kelayakan}")
    
    # Akses breakdown detail
    for dim in breakdown['dimensi']:
        print(f"{dim['nama']}: {dim['skor']}/{dim['skor_maks']}")
        for param in dim['detail']:
            print(f"  - {param['parameter']}: {param['nilai']} (skor: {param['skor']})")
```

### HTTP Request
```bash
curl -X POST "http://localhost:8000/api/pesantren-scoring/{pesantren_id}/calculate" \
  -H "Authorization: Bearer <token>"
```

## Testing
Run test untuk verifikasi breakdown:
```bash
python test_pesantren_breakdown.py
```

Test ini akan:
1. Mengambil sample pesantren dari database
2. Menghitung scoring dengan breakdown
3. Memverifikasi struktur breakdown
4. Menyimpan hasil ke file JSON untuk inspeksi

## Perubahan dari Versi Sebelumnya

### Yang Berubah:
1. **Return Type**: Service methods sekarang mengembalikan `Tuple[PesantrenSkor, Dict[str, Any]]` (sebelumnya hanya `PesantrenSkor`)
2. **API Response**: Endpoint sekarang mengembalikan objek dengan `skor` dan `breakdown` (sebelumnya hanya `skor`)
3. **Detail Parameter**: Setiap parameter sekarang mencantumkan nilai aktual dan skor yang didapat

### Backward Compatibility:
- Endpoint lama masih berfungsi, tetapi sekarang mengembalikan struktur yang diperluas
- Database schema tidak berubah
- Kode yang hanya menggunakan `PesantrenSkor` object tetap kompatibel

## Tips Penggunaan

1. **Debugging**: Gunakan breakdown untuk melihat parameter mana yang berkontribusi pada skor rendah
2. **Reporting**: Breakdown dapat digunakan untuk membuat laporan detail kondisi pesantren
3. **Data Validation**: Periksa parameter dengan skor 0 atau "Tidak ada data" untuk identifikasi data yang belum lengkap
4. **Prioritas Perbaikan**: Fokus pada dimensi dengan skor rendah dan bobot tinggi untuk impact maksimal

## File Terkait

- **Service**: `app/services/pesantren_score_service.py`
- **Scoring Rules**: `app/rules/pesantren_scoring_rules.py`
- **Configuration**: `app/rules/pesantren_scoring.json`
- **API Routes**: `app/routes/pesantren_score_routes.py`
- **Repository**: `app/repositories/pesantren_data_repository.py`
- **Test Script**: `test_pesantren_breakdown.py`
