# Fix Summary: Pesantren Scoring Schema Mismatch

## Problem
The pesantren scoring API endpoint was returning a 500 error with the following message:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column pesantren_skor.skor_kelayakan_fisik does not exist
```

## Root Cause
A migration file (`20260101_add_missing_columns.py`) renamed the database column `skor_kelayakan_fisik` to `skor_fisik`, but the SQLAlchemy model and schema definitions were not updated to reflect this change. This created a schema mismatch between:
- **Database**: Used column name `skor_fisik`
- **SQLAlchemy Model**: Expected column name `skor_kelayakan_fisik`

## Solution
Updated three files to align with the database schema:

### 1. Model Definition (`app/models/pesantren_skor.py`)
- Changed column definition from `skor_kelayakan_fisik` to `skor_fisik`
- Added new optional columns: `skor_fasilitas` and `skor_pendidikan`

### 2. Pydantic Schema (`app/schemas/pesantren_skor_schema.py`)
- Updated `PesantrenSkorBase` schema field from `skor_kelayakan_fisik` to `skor_fisik`
- Added optional fields for `skor_fasilitas` and `skor_pendidikan`

### 3. Service Layer (`app/services/pesantren_score_service.py`)
- Updated both `create` and `update` operations to use `skor_fisik` when persisting to database
- Maintained mapping: `skor_fisik=per_dimension["skor_kelayakan_fisik"]` (internal scoring rules still use the descriptive name)

## Verification
✅ Schema validation completed:
- All database columns match the SQLAlchemy model
- Query test successful with sample data
- Model-to-schema mapping is consistent

## Testing
To verify the fix works, test the endpoint:
```bash
GET /api/pesantren-scoring/pesantren/{pesantren_id}
```

The endpoint should now return a 200 status with the pesantren scoring data instead of a 500 error.

## Note on Column Naming
The scoring calculation rules (`pesantren_scoring_rules.py`) continue to use `skor_kelayakan_fisik` in the `per_dimension` dictionary. This is acceptable because:
1. It's an internal calculation dictionary
2. The mapping to the database column `skor_fisik` is handled in the service layer
3. The API schema now correctly reflects what's in the database
