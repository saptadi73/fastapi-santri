# Changelog - Scoring System Updates

## Tanggal: 1 Januari 2026

### Overview Perubahan
Sistem scoring untuk santri dan pesantren telah diupdate dengan **breakdown detail yang komprehensif** dan **perbaikan kalkulasi total skor** untuk transparansi dan akurasi yang lebih baik.

---

## 🎯 Santri Scoring - Perubahan Major

### 1. Perbaikan Kalkulasi Total Skor

**SEBELUM:**
- `skor_total` = weighted sum (bobot × skor dimensi)
- Contoh: (30% × 25) + (25% × 22) + ... = 17

**SEKARANG:**
- `skor_total` = **sum of raw dimension scores**
- Contoh: 25 + 22 + 23 + 2 + 0 + 11 = **83**

**Alasan Perubahan:**
- UI menampilkan total komponen = 83
- Backend menyimpan total weighted = 17
- Mismatch membingungkan dan tidak transparan
- Raw sum lebih intuitif dan mudah dipahami

**Impact:**
- Nilai `skor_total` akan lebih tinggi (karena sum, bukan weighted average)
- Kategori kemiskinan masih tetap akurat dengan threshold yang sudah disesuaikan
- Frontend tidak perlu perubahan logic jika sudah menampilkan sum komponen

### 2. Tambahan Breakdown Detail

**Response Structure Baru:**
```json
{
  "success": true,
  "message": "Skor berhasil dihitung dan disimpan",
  "data": {
    "skor": {
      "id": "uuid",
      "santri_id": "uuid",
      "skor_ekonomi": 25,
      "skor_rumah": 22,
      "skor_aset": 23,
      "skor_pembiayaan": 2,
      "skor_kesehatan": 0,
      "skor_bansos": 11,
      "skor_total": 83,
      "kategori_kemiskinan": "Sangat Miskin",
      "metode": "pesantren_kemiskinan_v1",
      "version": "1.0.0"
    },
    "breakdown": {
      "dimensi": [...],
      "skor_total": 83,
      "kategori_kemiskinan": "Sangat Miskin",
      "interpretasi_kategori": "Kondisi sangat buruk, memerlukan bantuan segera"
    }
  }
}
```

### 3. Detail Breakdown Per Dimensi

Setiap dimensi sekarang menampilkan:
- **nama**: Nama dimensi yang user-friendly
- **skor**: Skor aktual dimensi (raw score, bukan weighted)
- **skor_maks**: Maximum possible score untuk dimensi
- **bobot**: Bobot dimensi dalam persen (untuk referensi)
- **kontribusi**: Skor aktual (bukan weighted, untuk konsistensi dengan total)
- **interpretasi**: Kondisi dimensi (Sangat Baik, Baik, Sedang, Buruk, Sangat Buruk)
- **detail**: Array parameter dengan nilai dan skor masing-masing

**Interpretasi Dimensi:**
- **Sangat Baik**: Skor = 0 (tidak ada masalah)
- **Baik**: Skor ≤ 25% dari skor_maks
- **Sedang**: Skor ≤ 50% dari skor_maks
- **Buruk**: Skor ≤ 75% dari skor_maks
- **Sangat Buruk**: Skor > 75% dari skor_maks

### 4. Detail Parameter

Setiap parameter dalam dimensi menampilkan:
```json
{
  "parameter": "Pendapatan Bulanan",
  "nilai": "800000",
  "skor": 25
}
```

**Benefit:**
- Dapat melihat nilai aktual yang digunakan untuk scoring
- Dapat trace kenapa santri mendapat skor tertentu
- Memudahkan validasi data dan identifikasi kesalahan input

---

## 🏫 Pesantren Scoring - Tambahan Breakdown Detail

### 1. Response Structure Baru

**SEBELUM:**
```json
{
  "id": "uuid",
  "pesantren_id": "uuid",
  "skor_fisik": 98,
  "skor_total": 94,
  "kategori_kelayakan": "sangat_layak"
}
```

**SEKARANG:**
```json
{
  "success": true,
  "data": {
    "skor": {
      "id": "uuid",
      "pesantren_id": "uuid",
      "skor_fisik": 98,
      "skor_air_sanitasi": 100,
      "skor_fasilitas_pendukung": 83,
      "skor_mutu_pendidikan": 93,
      "skor_total": 94,
      "kategori_kelayakan": "sangat_layak"
    },
    "breakdown": {
      "dimensi": [...],
      "skor_total": 94,
      "kategori_kelayakan": "sangat_layak",
      "interpretasi_kategori": "Kondisi sangat baik, memenuhi semua standar kelayakan"
    }
  }
}
```

### 2. Detail Breakdown Per Dimensi

Struktur sama dengan santri scoring:
- **nama**: "Kelayakan Fisik Bangunan", "Air Bersih dan Sanitasi", dll
- **skor**: Skor dimensi (0-100, higher = better)
- **skor_maks**: 100 (semua dimensi dinormalisasi ke 0-100)
- **bobot**: Persentase bobot (40%, 25%, 20%, 15%)
- **kontribusi**: Kontribusi ke weighted total
- **interpretasi**: Sangat Baik, Baik, Cukup, Kurang
- **detail**: Array parameter dengan nilai dan skor

**Interpretasi Dimensi:**
- **Sangat Baik**: Skor ≥ 85
- **Baik**: Skor 70-84
- **Cukup**: Skor 55-69
- **Kurang**: Skor < 55

### 3. Perbedaan dengan Santri Scoring

| Aspek | Santri Scoring | Pesantren Scoring |
|-------|----------------|-------------------|
| Total Calculation | Sum of raw scores | Weighted average |
| Skor Range | 0-168 (sum of all maks) | 0-100 (normalized) |
| Higher Score Means | More vulnerable/poor | Better quality |
| Dimensi Maks | Berbeda per dimensi | Semua 100 (normalized) |

---

## 📝 File yang Dimodifikasi

### Santri Scoring
1. **app/rules/scoring_rules.py**
   - Modified `calculate_scores_from_config()` to sum raw scores instead of weighted
   - Added breakdown generation with interpretations
   - Added parameter detail collection

2. **app/services/score_service.py**
   - Return type changed to `Tuple[SantriSkor, Dict[str, Any]]`
   - `calculate_and_save()` returns (record, breakdown)
   - `get_by_santri_id()` returns (record, breakdown)

3. **app/routes/santri_score_routes.py** (if exists)
   - Updated to handle tuple returns
   - Response includes both skor and breakdown

### Pesantren Scoring
1. **app/rules/pesantren_scoring_rules.py**
   - Modified `calculate_dimension_score()` to return `Tuple[int, list]`
   - Added parameter detail collection with friendly names
   - Modified `calculate_pesantren_scores_from_config()` to return breakdown

2. **app/services/pesantren_score_service.py**
   - Return type changed to `Tuple[PesantrenSkor, Dict[str, Any]]`
   - `calculate_and_save()` returns (record, breakdown)
   - `get_by_pesantren_id()` returns (record, breakdown)

3. **app/routes/pesantren_score_routes.py**
   - Updated all endpoints to return `{skor: ..., breakdown: ...}`
   - POST `/calculate` returns breakdown
   - GET `/pesantren/{id}` returns breakdown

### Dokumentasi
1. **app/docs/API_DOCUMENTATION.md**
   - Updated santri scoring response examples
   - Updated pesantren scoring response examples
   - Added breakdown field explanations
   - Clarified total score calculations

2. **PESANTREN_SCORING_BREAKDOWN.md** (NEW)
   - Comprehensive guide for pesantren breakdown
   - Structure documentation
   - Usage examples
   - Testing instructions

### Test Files
1. **test_pesantren_breakdown.py** (NEW)
   - Comprehensive test for pesantren scoring
   - Validates breakdown structure
   - Exports sample JSON
   - Verifies data consistency

---

## 🔧 Migration Guide

### Backend Changes Required

#### 1. Update API Calls
**SEBELUM:**
```python
record = service.calculate_and_save(santri_id)
print(record.skor_total)
```

**SEKARANG:**
```python
record, breakdown = service.calculate_and_save(santri_id)
print(record.skor_total)
print(breakdown['kategori_kemiskinan'])
```

#### 2. Update Response Handling
**SEBELUM:**
```javascript
const response = await axios.post(`/api/scoring/${id}/calculate`);
const score = response.data.data.skor_total;
```

**SEKARANG:**
```javascript
const response = await axios.post(`/api/scoring/${id}/calculate`);
const score = response.data.data.skor.skor_total;
const breakdown = response.data.data.breakdown;
```

### Frontend Changes Required

#### 1. Update Score Display
```javascript
// Display main score
const { skor, breakdown } = response.data.data;
displayScore(skor.skor_total);
displayCategory(skor.kategori_kemiskinan);

// Display breakdown
breakdown.dimensi.forEach(dim => {
  console.log(`${dim.nama}: ${dim.skor}/${dim.skor_maks}`);
  console.log(`Interpretasi: ${dim.interpretasi}`);
  
  // Show parameter details
  dim.detail?.forEach(param => {
    console.log(`  - ${param.parameter}: ${param.nilai} (skor: ${param.skor})`);
  });
});
```

#### 2. Display Interpretations
```javascript
// Show overall interpretation
<div class="kategori-info">
  <h3>{breakdown.kategori_kemiskinan}</h3>
  <p>{breakdown.interpretasi_kategori}</p>
</div>

// Show dimension breakdown
{breakdown.dimensi.map(dim => (
  <div key={dim.nama} class="dimension-card">
    <h4>{dim.nama}</h4>
    <div class="score-bar">
      <div style={{width: `${(dim.skor / dim.skor_maks) * 100}%`}}></div>
    </div>
    <p class="score">{dim.skor} / {dim.skor_maks}</p>
    <p class="interpretation">{dim.interpretasi}</p>
    
    {/* Parameter details */}
    <ul class="param-list">
      {dim.detail?.map(param => (
        <li key={param.parameter}>
          <span>{param.parameter}:</span>
          <span>{param.nilai}</span>
          <span class="param-score">{param.skor}</span>
        </li>
      ))}
    </ul>
  </div>
))}
```

---

## ✅ Testing

### Santri Scoring Test
```bash
# Via Python script
python -c "
from uuid import UUID
from app.core.database import SessionLocal
from app.services.score_service import ScoreService
import importlib, pkgutil
import app.models as models_pkg

[importlib.import_module(f'app.models.{m.name}') for m in pkgutil.iter_modules(models_pkg.__path__)]

with SessionLocal() as db:
    svc = ScoreService(db)
    santri_id = UUID('your-santri-id-here')
    rec, breakdown = svc.calculate_and_save(santri_id)
    print(f'Total: {rec.skor_total}')
    print(f'Kategori: {rec.kategori_kemiskinan}')
    print(f'Breakdown dimensi: {len(breakdown[\"dimensi\"])}')
"
```

### Pesantren Scoring Test
```bash
# Run dedicated test script
python test_pesantren_breakdown.py
```

Expected output:
- Skor total calculation correct
- Breakdown includes 4/6 dimensi (santri/pesantren)
- Each dimension has detail parameters
- Interpretations are present
- Data consistency verified

---

## 🚨 Breaking Changes

### API Response Structure
- **OLD**: Scoring endpoints returned flat score object
- **NEW**: Scoring endpoints return `{skor: {...}, breakdown: {...}}`

### Service Method Returns
- **OLD**: `calculate_and_save()` returns `SkorModel`
- **NEW**: `calculate_and_save()` returns `Tuple[SkorModel, Dict]`

### Migration Required
- Update all code that calls scoring services
- Update frontend to handle new response structure
- Update any tests that check scoring responses

---

## 📚 Documentation References

1. **API Documentation**: `/app/docs/API_DOCUMENTATION.md`
   - Santri Scoring section (updated)
   - Pesantren Scoring section (updated)

2. **Pesantren Breakdown Guide**: `/PESANTREN_SCORING_BREAKDOWN.md`
   - Detailed breakdown structure
   - Parameter explanations
   - Usage examples

3. **Test Scripts**:
   - `test_pesantren_breakdown.py` - Comprehensive pesantren test
   - Inline Python snippets for santri testing

---

## 🎉 Benefits

### For Developers
✅ Type-safe returns with tuple unpacking
✅ Detailed breakdown for debugging
✅ Clear traceability of score calculations
✅ Consistent structure across santri and pesantren scoring

### For Users
✅ Transparent scoring - can see how scores are calculated
✅ Parameter-level details help identify data issues
✅ Interpretations provide context without needing to know scoring rules
✅ Better understanding of poverty/quality assessment

### For System
✅ Improved data validation through visibility
✅ Easier troubleshooting of scoring issues
✅ Better audit trail for scoring decisions
✅ Foundation for future scoring improvements

---

## 📞 Support

Jika ada pertanyaan atau issues terkait perubahan ini:
1. Check API_DOCUMENTATION.md untuk detail endpoint
2. Check PESANTREN_SCORING_BREAKDOWN.md untuk pesantren specifics
3. Run test scripts untuk validate changes
4. Review changelog ini untuk understand breaking changes

---

**Version**: 2.0.0
**Date**: 1 Januari 2026
**Status**: ✅ Completed
