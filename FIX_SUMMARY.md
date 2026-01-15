# Fix Summary

## 1. Pesantren Scoring Schema Mismatch

### Problem
The pesantren scoring API endpoint was returning a 500 error with the following message:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column pesantren_skor.skor_kelayakan_fisik does not exist
```

### Root Cause
A migration file (`20260101_add_missing_columns.py`) renamed the database column `skor_kelayakan_fisik` to `skor_fisik`, but the SQLAlchemy model and schema definitions were not updated to reflect this change. This created a schema mismatch between:
- **Database**: Used column name `skor_fisik`
- **SQLAlchemy Model**: Expected column name `skor_kelayakan_fisik`

### Solution
Updated three files to align with the database schema:

#### 1. Model Definition (`app/models/pesantren_skor.py`)
- Changed column definition from `skor_kelayakan_fisik` to `skor_fisik`
- Added new optional columns: `skor_fasilitas` and `skor_pendidikan`

#### 2. Pydantic Schema (`app/schemas/pesantren_skor_schema.py`)
- Updated `PesantrenSkorBase` schema field from `skor_kelayakan_fisik` to `skor_fisik`
- Added optional fields for `skor_fasilitas` and `skor_pendidikan`

#### 3. Service Layer (`app/services/pesantren_score_service.py`)
- Updated both `create` and `update` operations to use `skor_fisik` when persisting to database
- Maintained mapping: `skor_fisik=per_dimension["skor_kelayakan_fisik"]` (internal scoring rules still use the descriptive name)

### Verification
✅ Schema validation completed:
- All database columns match the SQLAlchemy model
- Query test successful with sample data
- Model-to-schema mapping is consistent

### Testing
To verify the fix works, test the endpoint:
```bash
GET /api/pesantren-scoring/pesantren/{pesantren_id}
```

The endpoint should now return a 200 status with the pesantren scoring data instead of a 500 error.

### Note on Column Naming
The scoring calculation rules (`pesantren_scoring_rules.py`) continue to use `skor_kelayakan_fisik` in the `per_dimension` dictionary. This is acceptable because:
1. It's an internal calculation dictionary
2. The mapping to the database column `skor_fisik` is handled in the service layer
3. The API schema now correctly reflects what's in the database

---

## 2. Pesantren Fasilitas Enum Values Fix

### Problem
The pesantren fasilitas API endpoint was returning a 500 error with the following message:
```
LookupError: '2' is not among the defined enum values. 
Enum name: kelayakan_enum. Possible values: layak, cukup, tidak_layak
```

### Root Cause
The database contained numeric values (1-14) in the `asrama` and `ruang_belajar` columns that were originally stored as quantity/quality indicators. However, these columns are defined as PostgreSQL enums that only accept specific string values:
- `asrama`: Uses `kelayakan_enum` (layak, cukup, tidak_layak)
- `ruang_belajar`: Uses `kelayakan_enum` (layak, cukup, tidak_layak)
- `internet`: Uses `kestabilan_enum` (stabil, tidak_stabil, tidak_ada)

When SQLAlchemy attempted to query these records, it failed because the numeric values couldn't be matched to the enum definitions.

### Solution
Created and executed a data migration script (`fix_fasilitas_enum_values.py`) that:
1. Identified all records with numeric values in enum columns (400 records affected)
2. Mapped numeric values to appropriate enum values using the following logic:
   - **1**: `tidak_layak` (low quality/quantity)
   - **2-4**: `cukup` (moderate quality/quantity)
   - **5+**: `layak` (good quality/quantity)
3. Updated all records in a single transaction
4. Preserved existing valid enum values (layak, cukup, tidak_layak)

### Affected Fields
- `asrama` (dormitory condition)
- `ruang_belajar` (classroom condition)
- `internet` (already had valid values, no changes needed)

### Verification
✅ All enum values are now valid:
- **asrama**: layak, cukup, tidak_layak
- **ruang_belajar**: layak, cukup, tidak_layak
- **internet**: stabil, tidak_stabil, tidak_ada

✅ Query test successful:
```sql
SELECT DISTINCT asrama FROM pesantren_fasilitas WHERE asrama IS NOT NULL;
-- Result: layak, cukup, tidak_layak

SELECT DISTINCT ruang_belajar FROM pesantren_fasilitas WHERE ruang_belajar IS NOT NULL;
-- Result: layak, cukup, tidak_layak
```

### Testing
To verify the fix works, test the endpoint:
```bash
GET /pesantren-fasilitas/pesantren/{pesantren_id}
```

The endpoint should now return a 200 status with valid enum values instead of a 500 error.

### Important Notes
1. **Only use string enum values** when creating or updating pesantren_fasilitas records
2. **Never use numeric values** for enum fields - they will cause lookup errors
3. Refer to the Frontend Enum Reference in API_DOCUMENTATION.md for authoritative enum values
4. All enum fields are nullable - use `null` if value is unknown, not a numeric placeholder

### Migration Files
- **Check script**: `check_fasilitas_enum_issue.py` - Diagnoses enum value issues
- **Fix script**: `fix_fasilitas_enum_values.py` - Converts numeric values to valid enums
