# 🗄️ DBA QUICK REFERENCE - Production Deployment 2026-01-17

## 📌 Critical Information

| Item | Value |
|------|-------|
| Deployment Date | 2026-01-17 |
| Main SQL File | `PRODUCTION_DB_MIGRATION_2026_01_17.sql` |
| Rollback Script | `PRODUCTION_ROLLBACK_SCRIPT_2026_01_17.sql` |
| Estimated Duration | 15-30 minutes |
| Risk Level | LOW (additive only, no data loss) |
| Backup Required | YES - CRITICAL |
| Testing Environment | Staging (pre-tested) |

## 🚨 Pre-Flight Commands

```bash
# 1. Verify backup exists
ls -lh santri_db_backup_2026_01_17.dump

# 2. Check database size
psql -h production-host -U postgres -d santri_db -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# 3. Verify disk space
psql -h production-host -U postgres -d santri_db -c "SELECT * FROM pg_tablespace;"

# 4. Check active connections
psql -h production-host -U postgres -d santri_db -c "SELECT count(*) FROM pg_stat_activity WHERE datname='santri_db';"

# 5. Check long-running queries
psql -h production-host -U postgres -d santri_db -c "SELECT pid, query, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

## 🎯 Deployment Commands (One-liner)

### Full Automated Deployment
```bash
# Complete migration with logging
psql -h production-host -U postgres -d santri_db \
  -v ON_ERROR_STOP=1 \
  -f PRODUCTION_DB_MIGRATION_2026_01_17.sql \
  > migration_$(date +%Y%m%d_%H%M%S).log 2>&1 && echo "Migration completed successfully" || echo "Migration failed - check logs"
```

### Gradual Deployment (Step-by-Step)
```bash
# Step 1: Extensions
psql -h production-host -U postgres -d santri_db << 'EOF'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
SELECT * FROM pg_extension;
EOF

# Step 2: Enum types
psql -h production-host -U postgres -d santri_db -f sections/enums.sql

# Step 3: Map tables
psql -h production-host -U postgres -d santri_db -f sections/tables.sql

# Step 4: Indexes
psql -h production-host -U postgres -d santri_db -f sections/indexes.sql

# Step 5: Triggers & Views
psql -h production-host -U postgres -d santri_db -f sections/triggers_views.sql
```

## ✅ Post-Deployment Verification

### Quick Checks (Run immediately after)
```bash
# Check extensions
psql -h production-host -U postgres -d santri_db -c "\dx"

# Check tables
psql -h production-host -U postgres -d santri_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('santri_map', 'pesantren_map', 'gemini_ask_log');"

# Count indexes
psql -h production-host -U postgres -d santri_db -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public' AND (tablename IN ('santri_map', 'pesantren_map'));"

# Check views
psql -h production-host -U postgres -d santri_db -c "SELECT matviewname FROM pg_matviews WHERE schemaname='public';"

# Check triggers
psql -h production-host -U postgres -d santri_db -c "SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema='public';"
```

### Detailed Validation
```bash
# Validate all objects created
psql -h production-host -U postgres -d santri_db << 'EOF'
-- Extensions (should show 4+)
\echo '=== EXTENSIONS ==='
SELECT extname FROM pg_extension WHERE extname IN ('postgis', 'pgcrypto', 'uuid-ossp', 'pg_trgm');

-- Tables (should show 3)
\echo '=== TABLES ==='
SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('santri_map', 'pesantren_map', 'gemini_ask_log');

-- Indexes (should show 30+)
\echo '=== INDEXES ==='
SELECT COUNT(*) as index_count FROM pg_indexes WHERE schemaname='public' AND (tablename IN ('santri_map', 'pesantren_map', 'gemini_ask_log') OR indexname LIKE '%kategori%' OR indexname LIKE '%skor%');

-- Materialized Views (should show 2)
\echo '=== MATERIALIZED VIEWS ==='
SELECT matviewname FROM pg_matviews WHERE schemaname='public';

-- Triggers (should show 2)
\echo '=== TRIGGERS ==='
SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema='public' AND event_object_table IN ('santri_skor', 'pesantren_skor');
EOF
```

## 🔄 Materialized View Refresh

```bash
# Refresh views after migration (takes 1-5 minutes)
psql -h production-host -U postgres -d santri_db << 'EOF'
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_santri_stats_kabupaten;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pesantren_stats_kabupaten;

-- Check view row counts
SELECT COUNT(*) FROM mv_santri_stats_kabupaten;
SELECT COUNT(*) FROM mv_pesantren_stats_kabupaten;
EOF

# Schedule automatic refresh (add to crontab)
# 0 * * * * psql -h production-host -U postgres -d santri_db -c "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_santri_stats_kabupaten; REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pesantren_stats_kabupaten;" 2>/dev/null
```

## 🆘 Troubleshooting

### Problem: PostGIS Extension Won't Install
```bash
# Check if PostgreSQL contrib packages are installed
apt-cache policy postgresql-contrib

# Install if needed
sudo apt-get install postgresql-contrib postgresql-13-postgis

# Or on macOS
brew install postgis
```

### Problem: Migration Script Fails
```bash
# View detailed error
psql -h production-host -U postgres -d santri_db \
  -v ON_ERROR_STOP=1 \
  -f PRODUCTION_DB_MIGRATION_2026_01_17.sql

# Check specific section
psql -h production-host -U postgres -d santri_db << 'EOF'
-- Test extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOF

# Check database logs
tail -100 /var/log/postgresql/postgresql.log
```

### Problem: Indexes Not Being Used
```bash
# Disable parallel query if indexes still not used
psql -h production-host -U postgres -d santri_db << 'EOF'
SET max_parallel_workers_per_gather = 0;
ANALYZE santri_map;
ANALYZE pesantren_map;

-- Verify index usage
EXPLAIN ANALYZE
SELECT * FROM santri_map WHERE kategori_kemiskinan = 'Sangat Miskin' LIMIT 10;
EOF
```

### Problem: Slow Queries After Migration
```bash
# Check table statistics
psql -h production-host -U postgres -d santri_db << 'EOF'
ANALYZE;
ANALYZE santri_map;
ANALYZE pesantren_map;
REINDEX INDEX idx_santri_map_kategori_skor;
REINDEX INDEX idx_pesantren_map_kategori_skor;
EOF

# Check query plans
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM santri_map WHERE kategori_kemiskinan = 'Sangat Miskin';
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM pesantren_map WHERE kategori_kelayakan = 'layak';
```

## 📊 Performance Baseline Queries

```bash
# Get query performance before/after comparison
psql -h production-host -U postgres -d santri_db << 'EOF'
-- Top 10 slowest queries
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;

-- Index usage report
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Table scan analysis
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND (tablename LIKE '%santri%' OR tablename LIKE '%pesantren%')
ORDER BY seq_scan DESC;

-- Cache hit ratio
SELECT
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit)  as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;

-- Index size report
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
EOF
```

## 🔙 Rollback Commands

### Quick Rollback
```bash
# Restore from backup (safest option)
pg_restore -h production-host -U postgres -d santri_db \
  --clean \
  -v \
  santri_db_backup_2026_01_17.dump

# Or run rollback script (faster but verify first)
psql -h production-host -U postgres -d santri_db \
  -v ON_ERROR_STOP=1 \
  -f PRODUCTION_ROLLBACK_SCRIPT_2026_01_17.sql
```

### Verify Rollback Complete
```bash
psql -h production-host -U postgres -d santri_db << 'EOF'
-- Should return no rows if rollback successful
SELECT table_name FROM information_schema.tables 
WHERE table_schema='public' AND table_name IN ('santri_map', 'pesantren_map', 'gemini_ask_log');

-- Should return no rows
SELECT matviewname FROM pg_matviews WHERE schemaname='public' 
AND matviewname IN ('mv_santri_stats_kabupaten', 'mv_pesantren_stats_kabupaten');
EOF
```

## 📋 Important Notes

- **NO DATA LOSS**: Migration is additive only
- **BACKUP FIRST**: Always backup before running migration
- **TEST STAGING**: Pre-test on staging environment first
- **MONITORING**: Monitor closely for first 24 hours after deployment
- **MAINTENANCE**: Refresh materialized views after bulk data changes
- **PERFORMANCE**: Expect 50-90% query performance improvement

## 📞 Support

| Role | Contact | Phone |
|------|---------|-------|
| Database Admin | [Name] | [Phone] |
| Senior DBA | [Name] | [Phone] |
| DevOps Lead | [Name] | [Phone] |
| On-Call | [Name] | [Phone] |

## 📄 Related Files

- `PRODUCTION_DB_MIGRATION_2026_01_17.sql` - Main migration script
- `PRODUCTION_ROLLBACK_SCRIPT_2026_01_17.sql` - Rollback script
- `PRODUCTION_DEPLOYMENT_GUIDE_2026_01_17.md` - Full deployment guide
- `PRODUCTION_DEPLOYMENT_CHECKLIST_2026_01_17.md` - Deployment checklist
- `GIS_OPTIMIZATION_ANALYSIS.md` - Technical analysis
- `GEMINI_ASK_ENDPOINT_GUIDE.md` - New feature documentation

---

**Version**: 1.0.0  
**Date**: 2026-01-17  
**Status**: Ready for DBA Review
