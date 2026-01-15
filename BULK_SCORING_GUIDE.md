# Bulk Scoring Guide

## Quick Start

Untuk melakukan re-scoring semua data santri dan pesantren sekaligus:

```bash
# Pastikan server FastAPI berjalan
uvicorn app.main:app --reload

# Di terminal lain, jalankan:
python bulk_scoring.py
```

## API Endpoints

### 1. Recalculate All Santri Scores

```bash
POST /api/scoring/batch/calculate-all
```

**Response:**
```json
{
  "success": true,
  "message": "Scoring selesai: 400 berhasil, 0 gagal",
  "data": {
    "total_processed": 400,
    "total_errors": 0,
    "results": [
      {
        "santri_id": "867c0a86-85e3-4490-abab-1b2d4e8e13c2",
        "nama": "Ahmad Santoso",
        "skor_total": 45,
        "kategori": "Miskin"
      },
      ...
    ],
    "errors": []
  }
}
```

### 2. Recalculate All Pesantren Scores

```bash
POST /api/pesantren-scoring/batch/calculate-all
```

**Response:**
```json
{
  "success": true,
  "message": "Scoring selesai: 50 berhasil, 0 gagal",
  "data": {
    "total_processed": 50,
    "total_errors": 0,
    "results": [
      {
        "pesantren_id": "550e8400-e29b-41d4-a716-446655440000",
        "nama": "Pesantren Al-Ikhlas",
        "skor_total": 65,
        "kategori": "Layak"
      },
      ...
    ],
    "errors": []
  }
}
```

## Using cURL

### Santri Batch Scoring
```bash
curl -X POST http://localhost:8000/api/scoring/batch/calculate-all
```

### Pesantren Batch Scoring
```bash
curl -X POST http://localhost:8000/api/pesantren-scoring/batch/calculate-all
```

## Using Python Script

File `bulk_scoring.py` sudah disediakan untuk kemudahan:

```python
# Install dependencies terlebih dahulu
pip install requests

# Run the script
python bulk_scoring.py
```

Script akan:
1. ✓ Recalculate semua santri scores
2. ✓ Recalculate semua pesantren scores
3. ✓ Tampilkan summary hasil dan waktu proses
4. ✓ Tampilkan error jika ada

## When to Use Bulk Scoring

Gunakan bulk scoring ketika:
- ✅ Setelah import/update data santri atau pesantren dalam jumlah besar
- ✅ Setelah mengubah enum values (seperti fix yang baru saja dilakukan)
- ✅ Setelah update aturan scoring
- ✅ Setup awal database dengan dummy data
- ✅ Migrasi data dari sistem lama

## Performance

Untuk referensi (dapat bervariasi tergantung hardware):
- **400 santri**: ~10-20 detik
- **50 pesantren**: ~3-5 detik
- **Total**: ~15-25 detik untuk semua data

## Notes

- ⚠️ Endpoint ini akan **overwrite** semua skor yang ada
- ✅ Proses berjalan secara sequential (satu per satu) untuk memastikan konsistensi
- ✅ Jika ada error pada satu record, proses tetap berlanjut untuk record lainnya
- ✅ Error details akan dikembalikan dalam response
