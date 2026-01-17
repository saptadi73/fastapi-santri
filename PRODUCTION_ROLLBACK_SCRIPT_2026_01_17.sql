-- ============================================================================
-- PRODUCTION ROLLBACK SCRIPT - 2026-01-17
-- ============================================================================
-- This script can be used to rollback the production migration if issues occur.
-- CAUTION: Use only if there are critical issues with the migration.
-- 
-- IMPORTANT: This script drops new tables and indexes. Data in new tables will
-- be lost, but data in existing tables remains intact.
-- ============================================================================

-- ============================================================================
-- SECTION 1: STOP TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS trg_update_santri_map_on_skor_change ON santri_skor;
DROP TRIGGER IF EXISTS trg_update_pesantren_map_on_skor_change ON pesantren_skor;

-- ============================================================================
-- SECTION 2: DROP MATERIALIZED VIEWS
-- ============================================================================

DROP MATERIALIZED VIEW IF EXISTS mv_santri_stats_kabupaten CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_pesantren_stats_kabupaten CASCADE;

-- ============================================================================
-- SECTION 3: DROP TRIGGER FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS fn_update_santri_map_on_skor_change();
DROP FUNCTION IF EXISTS fn_update_pesantren_map_on_skor_change();

-- ============================================================================
-- SECTION 4: DROP NEW INDEXES
-- ============================================================================

-- Santri Map Indexes
DROP INDEX IF EXISTS idx_santri_map_lokasi;
DROP INDEX IF EXISTS idx_santri_map_santri_id;
DROP INDEX IF EXISTS idx_santri_map_nama;
DROP INDEX IF EXISTS idx_santri_map_pesantren_id;
DROP INDEX IF EXISTS idx_santri_map_kategori_skor;
DROP INDEX IF EXISTS idx_santri_map_lokasi_admin;

-- Pesantren Map Indexes
DROP INDEX IF EXISTS idx_pesantren_map_lokasi;
DROP INDEX IF EXISTS idx_pesantren_map_pesantren_id;
DROP INDEX IF EXISTS idx_pesantren_map_nama;
DROP INDEX IF EXISTS idx_pesantren_map_kabupaten;
DROP INDEX IF EXISTS idx_pesantren_map_provinsi;
DROP INDEX IF EXISTS idx_pesantren_map_kategori_skor;

-- Additional Optimization Indexes (created in migration)
DROP INDEX IF EXISTS idx_santri_pribadi_kabupaten;
DROP INDEX IF EXISTS idx_santri_pribadi_provinsi;
DROP INDEX IF EXISTS idx_santri_pribadi_kecamatan;
DROP INDEX IF EXISTS idx_pondok_pesantren_kabupaten;
DROP INDEX IF EXISTS idx_pondok_pesantren_provinsi;
DROP INDEX IF EXISTS idx_pondok_pesantren_admin;
DROP INDEX IF EXISTS idx_santri_skor_santri_id;
DROP INDEX IF EXISTS idx_santri_skor_kategori;
DROP INDEX IF EXISTS idx_pesantren_skor_pesantren_id;
DROP INDEX IF EXISTS idx_pesantren_skor_kategori;

-- Text Search Optimization Indexes
DROP INDEX IF EXISTS idx_santri_pribadi_nama_trgm;
DROP INDEX IF EXISTS idx_pondok_pesantren_nama_trgm;

-- ============================================================================
-- SECTION 5: DROP NEW TABLES
-- ============================================================================

DROP TABLE IF EXISTS santri_map CASCADE;
DROP TABLE IF EXISTS pesantren_map CASCADE;
DROP TABLE IF EXISTS gemini_ask_log CASCADE;

-- ============================================================================
-- SECTION 6: DROP EXTENSIONS (Optional)
-- ============================================================================
-- WARNING: Only drop extensions if you're sure no other databases need them
-- Comment out these lines if extensions are shared with other databases

-- DROP EXTENSION IF EXISTS pg_trgm;
-- DROP EXTENSION IF EXISTS "uuid-ossp";
-- DROP EXTENSION IF EXISTS pgcrypto;
-- DROP EXTENSION IF EXISTS postgis;

-- ============================================================================
-- SECTION 7: VERIFY ROLLBACK COMPLETE
-- ============================================================================

-- Verify tables are dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema='public' 
AND table_name IN ('santri_map', 'pesantren_map', 'gemini_ask_log');
-- Expected: No rows

-- Verify indexes are dropped
SELECT indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND (tablename IN ('santri_map', 'pesantren_map', 'gemini_ask_log'));
-- Expected: No rows

-- Verify materialized views are dropped
SELECT matviewname 
FROM pg_matviews 
WHERE schemaname = 'public'
AND matviewname IN ('mv_santri_stats_kabupaten', 'mv_pesantren_stats_kabupaten');
-- Expected: No rows

-- Verify triggers are dropped
SELECT trigger_name 
FROM information_schema.triggers 
WHERE trigger_schema = 'public'
AND trigger_name IN ('trg_update_santri_map_on_skor_change', 'trg_update_pesantren_map_on_skor_change');
-- Expected: No rows

-- ============================================================================
-- ROLLBACK COMPLETE
-- ============================================================================
-- If all verification queries return no rows, rollback is complete.
-- Original tables and data remain intact.
-- Application should now revert to previous version.
-- ============================================================================
