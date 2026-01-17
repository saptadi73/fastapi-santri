# 📋 PRODUCTION DEPLOYMENT CHECKLIST - 2026-01-17

**Deployment Date**: 2026-01-17  
**Deployment Team**: [Your Team]  
**Deployment Lead**: [Your Name]  
**Start Time**: ___________  
**End Time**: ___________  

---

## 🔐 PRE-DEPLOYMENT PHASE (Do this 1 day before)

### Communication
- [ ] Notify all stakeholders about planned deployment
- [ ] Schedule maintenance window (if needed)
- [ ] Prepare status page update
- [ ] Brief customer support team
- [ ] Have rollback plan ready

### Testing (Staging Environment)
- [ ] Run PRODUCTION_DB_MIGRATION_2026_01_17.sql on staging DB
- [ ] Verify all extensions created successfully
- [ ] Verify all tables created successfully
- [ ] Verify all indexes created successfully
- [ ] Run full test suite on staging
- [ ] Test Gemini Ask endpoint with various questions
- [ ] Test GIS/Map endpoints with new indexes
- [ ] Performance test: verify query time improvement
- [ ] Load test: simulate production traffic
- [ ] Check application logs for warnings/errors

### Infrastructure Checks
- [ ] Verify production database connection
- [ ] Verify backup storage space available
- [ ] Verify disk space on production server (minimum 10GB free)
- [ ] Verify CPU/Memory availability
- [ ] Check network connectivity to production

---

## 💾 BACKUP PHASE

### Database Backup
- [ ] **TIME**: ___________
- [ ] Create full database backup
  ```bash
  pg_dump -h production-host -U postgres -d santri_db -F c -f santri_db_backup_2026_01_17.dump
  ```
- [ ] Verify backup file size is reasonable
- [ ] Verify backup integrity
  ```bash
  pg_restore --list santri_db_backup_2026_01_17.dump | head
  ```
- [ ] Copy backup to secondary storage
- [ ] Document backup location: ___________

### Code Backup
- [ ] Create git tag for current production code
  ```bash
  git tag -a production-pre-2026-01-17 -m "Before 2026-01-17 deployment"
  git push origin production-pre-2026-01-17
  ```
- [ ] Verify tag created
- [ ] Document git tag: production-pre-2026-01-17

### Configuration Backup
- [ ] Backup current .env file
- [ ] Backup current requirements.txt
- [ ] Backup current alembic configuration
- [ ] Store backups securely

---

## 🗄️ DATABASE MIGRATION PHASE

### Pre-Migration Checks
- [ ] **TIME**: ___________
- [ ] Verify database is accessible
- [ ] Verify database password is correct
- [ ] Check database size
  ```sql
  SELECT pg_size_pretty(pg_database_size(current_database()));
  ```
- [ ] Check available disk space
  ```sql
  SELECT * FROM pg_tablespace;
  ```
- [ ] Verify no long-running queries
  ```sql
  SELECT pid, query, state FROM pg_stat_activity WHERE state != 'idle';
  ```

### Execute Migration
- [ ] **TIME**: ___________
- [ ] **ATTENTION**: Following person confirmed backup exists: ___________
- [ ] Run migration script
  ```bash
  psql -h production-host -U postgres -d santri_db \
    -v ON_ERROR_STOP=1 \
    -f PRODUCTION_DB_MIGRATION_2026_01_17.sql \
    > migration_output_$(date +%Y%m%d_%H%M%S).log 2>&1
  ```
- [ ] Check exit code (should be 0)
- [ ] Review migration log for errors
- [ ] Check migration duration: _____ minutes

### Post-Migration Verification
- [ ] **TIME**: ___________
- [ ] Verify extensions created
  ```sql
  SELECT * FROM pg_extension;
  ```
- [ ] Verify tables created
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema='public' AND table_name IN ('santri_map', 'pesantren_map', 'gemini_ask_log');
  ```
- [ ] Verify indexes created
  ```sql
  SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public' 
  AND (tablename='santri_map' OR tablename='pesantren_map');
  ```
- [ ] Verify triggers created
  ```sql
  SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema='public';
  ```
- [ ] Verify materialized views created
  ```sql
  SELECT matviewname FROM pg_matviews WHERE schemaname='public';
  ```
- [ ] Run database integrity check
  ```bash
  psql -h production-host -U postgres -d santri_db -c "REINDEX DATABASE santri_db;"
  ```

---

## 📝 CODE DEPLOYMENT PHASE

### Pull Latest Code
- [ ] **TIME**: ___________
- [ ] Navigate to application directory
- [ ] Verify current branch
  ```bash
  git branch -v
  ```
- [ ] Pull latest changes
  ```bash
  git pull origin main
  ```
- [ ] Verify changes downloaded
  ```bash
  git log --oneline -5
  ```

### Update Dependencies
- [ ] Activate virtual environment
  ```bash
  source venv/bin/activate  # Linux/Mac
  # or
  venv\Scripts\activate  # Windows
  ```
- [ ] Upgrade pip
  ```bash
  pip install --upgrade pip
  ```
- [ ] Install/update dependencies
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- [ ] Verify key packages installed
  ```bash
  pip list | grep -E "fastapi|google-genai|sqlalchemy|psycopg2"
  ```

### Code Verification
- [ ] Check for Python syntax errors
  ```bash
  python -m py_compile app/**/*.py
  ```
- [ ] Verify environment variables set correctly
  ```bash
  env | grep GEMINI_API_KEY
  env | grep DATABASE_URL
  ```

---

## 🔄 APPLICATION RESTART PHASE

### Stop Application
- [ ] **TIME**: ___________
- [ ] Stop FastAPI service
  ```bash
  systemctl stop fastapi-santri
  # or
  supervisorctl stop fastapi-santri
  ```
- [ ] Verify service stopped
  ```bash
  systemctl status fastapi-santri
  ```
- [ ] Wait for graceful shutdown (max 30 seconds)
- [ ] Kill any lingering processes if necessary
  ```bash
  pkill -f "uvicorn"
  ```

### Verify Service Stopped
- [ ] Check process list
  ```bash
  ps aux | grep uvicorn
  ```
- [ ] Verify no processes running
- [ ] Check ports are released
  ```bash
  netstat -tulpn | grep 8000
  ```

### Start Application
- [ ] **TIME**: ___________
- [ ] Start FastAPI service
  ```bash
  systemctl start fastapi-santri
  # or
  supervisorctl start fastapi-santri
  ```
- [ ] Wait for application to start (30-60 seconds)
- [ ] Verify service status
  ```bash
  systemctl status fastapi-santri
  ```

### Verify Application Started
- [ ] Check process running
  ```bash
  ps aux | grep uvicorn
  ```
- [ ] Check port listening
  ```bash
  netstat -tulpn | grep 8000
  ```
- [ ] Check logs for startup errors
  ```bash
  tail -100 /var/log/fastapi-santri/error.log
  ```

---

## ✅ HEALTH CHECK PHASE

### Application Health
- [ ] **TIME**: ___________
- [ ] Test API is responding
  ```bash
  curl -X GET "http://production-api/health" \
    -H "Accept: application/json" \
    -w "\nStatus: %{http_code}\n"
  ```
- [ ] Verify response status 200
- [ ] Test Gemini health endpoint
  ```bash
  curl -X GET "http://production-api/gemini/health" \
    -H "Accept: application/json"
  ```
- [ ] Test basic API endpoint
  ```bash
  curl -X GET "http://production-api/pondok-pesantren/dropdown" \
    -H "Accept: application/json"
  ```

### GIS/Map Endpoints
- [ ] Test santri map endpoints
  ```bash
  curl -X GET "http://production-api/gis/choropleth/stats" \
    -H "Accept: application/json"
  ```
- [ ] Test pesantren map endpoints
  ```bash
  curl -X GET "http://production-api/gis/choropleth/pesantren-kabupaten?provinsi=Jawa%20Barat" \
    -H "Accept: application/json"
  ```
- [ ] Verify response time < 2 seconds

### Gemini Ask Endpoint
- [ ] Test with valid question
  ```bash
  curl -X POST "http://production-api/gemini/ask" \
    -H "Content-Type: application/json" \
    -d '{"question": "Apa itu pesantren?"}'
  ```
- [ ] Verify 200 response with valid answer
- [ ] Test with prohibited topic
  ```bash
  curl -X POST "http://production-api/gemini/ask" \
    -H "Content-Type: application/json" \
    -d '{"question": "Apa pendapat tentang partai politik?"}'
  ```
- [ ] Verify response rejects the question gracefully

### Database Health
- [ ] Verify database connectivity from application
- [ ] Check database query performance
  ```sql
  EXPLAIN ANALYZE SELECT * FROM santri_map WHERE kategori_kemiskinan = 'Sangat Miskin' LIMIT 10;
  ```
- [ ] Verify indexes are being used in queries

### Application Logs
- [ ] Check for error logs
  ```bash
  tail -50 /var/log/fastapi-santri/error.log
  ```
- [ ] Check for warning logs
  ```bash
  grep -i warning /var/log/fastapi-santri/error.log | tail -10
  ```
- [ ] Verify no critical errors
- [ ] Check access logs for 500 errors
  ```bash
  tail -50 /var/log/fastapi-santri/access.log | grep " 500 "
  ```

---

## 📊 MONITORING PHASE (First 1 hour)

### Real-time Monitoring
- [ ] **TIME**: ___________
- [ ] Monitor application metrics (CPU, Memory, Disk)
  ```bash
  top -b -n 1 | head -20
  ```
- [ ] Monitor database metrics
  ```bash
  watch -n 5 "psql -h production-host -U postgres -d santri_db -c 'SELECT datname, usename, application_name, query, query_start FROM pg_stat_activity WHERE state != 'idle';'"
  ```
- [ ] Monitor application logs
  ```bash
  tail -f /var/log/fastapi-santri/access.log
  ```
- [ ] Check for any alerts/anomalies

### Performance Verification
- [ ] Verify query performance improved
  ```bash
  psql -h production-host -U postgres -d santri_db -c "SELECT query, calls, mean_time FROM pg_stat_statements WHERE query LIKE '%santri_map%' OR query LIKE '%pesantren_map%' ORDER BY mean_time DESC;"
  ```
- [ ] Verify index usage
  ```bash
  psql -h production-host -U postgres -d santri_db -c "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes WHERE tablename IN ('santri_map', 'pesantren_map') ORDER BY idx_scan DESC;"
  ```
- [ ] Compare with baseline metrics

---

## 🔍 FINAL VERIFICATION PHASE

### Data Integrity
- [ ] **TIME**: ___________
- [ ] Verify no data loss in existing tables
  ```sql
  SELECT COUNT(*) FROM santri_pribadi;
  SELECT COUNT(*) FROM pondok_pesantren;
  SELECT COUNT(*) FROM santri_skor;
  SELECT COUNT(*) FROM pesantren_skor;
  ```
- [ ] Compare counts with pre-migration values
- [ ] Spot check sample data
  ```sql
  SELECT * FROM santri_pribadi LIMIT 5;
  SELECT * FROM santri_map LIMIT 5;
  ```

### Functionality Testing
- [ ] Test create/read operations work correctly
- [ ] Test update operations work correctly
- [ ] Test delete operations work correctly
- [ ] Test filter/search operations work correctly
- [ ] Test pagination works correctly
- [ ] Test sorting works correctly

### Performance Baselines
- [ ] Measure and document query response times
- [ ] Compare with pre-deployment baseline
- [ ] Verify improvement >= 50% for map queries
- [ ] Document any unexpected slowness

---

## ✨ FINAL APPROVAL PHASE

### Sign-offs
- [ ] **Database Admin**: _____________ (Name/Date/Time)
  - Approval: [ ] ✓ Approved [ ] ✗ Issues Found
  - Comments: _____________________

- [ ] **DevOps/Infrastructure**: _____________ (Name/Date/Time)
  - Approval: [ ] ✓ Approved [ ] ✗ Issues Found
  - Comments: _____________________

- [ ] **QA/Testing**: _____________ (Name/Date/Time)
  - Approval: [ ] ✓ Approved [ ] ✗ Issues Found
  - Comments: _____________________

- [ ] **Project Lead**: _____________ (Name/Date/Time)
  - Approval: [ ] ✓ Approved [ ] ✗ Issues Found
  - Comments: _____________________

### Stakeholder Notification
- [ ] Update status page
- [ ] Notify customers of deployment completion
- [ ] Send deployment report to stakeholders
- [ ] Update internal wiki/documentation
- [ ] Post deployment summary in team channel

---

## 🎯 SUMMARY

**Deployment Status**: [ ] SUCCESS [ ] PARTIAL SUCCESS [ ] ROLLED BACK [ ] FAILED

**Total Duration**: _________ minutes

**Issues Encountered**: [ ] None [ ] Minor [ ] Major

**Notes & Comments**:
```
[Add any important notes here]
```

**Next Steps**:
- [ ] Monitor production for 24 hours
- [ ] Schedule post-deployment review
- [ ] Update documentation
- [ ] Plan optimization tasks

---

## 📞 EMERGENCY CONTACTS

**Database Admin**: [Phone/Email]  
**DevOps Lead**: [Phone/Email]  
**Application Owner**: [Phone/Email]  
**On-Call Engineer**: [Phone/Email]  
**Manager**: [Phone/Email]  

---

**Deployment ID**: PROD-2026-01-17-001  
**Checklist Version**: 1.0.0  
**Last Updated**: 2026-01-17  
**Created By**: GitHub Copilot  
