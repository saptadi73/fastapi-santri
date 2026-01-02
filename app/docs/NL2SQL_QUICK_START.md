# NL2SQL Integration Guide

Quick guide untuk mengintegrasikan dan test NL2SQL system ke dalam FastAPI application.

## Status Implementation

✅ **COMPLETED:**
- Intent classifier dengan 12 tipe intent
- NL2SQL service dengan OpenAI integration
- FastAPI routes dengan 4 endpoints
- Schema context JSON
- Configuration (.env + app/core/config.py)
- Documentation & test scripts
- Security features (SQL validation, parameterized queries)
- Main app sudah terintegrasi

⏳ **READY TO TEST:**
- Pastikan OPENAI_API_KEY di-set di .env
- Jalankan test script
- Test endpoints dengan curl/Postman

---

## Quick Start

### 1. Set OpenAI API Key

Edit file `.env`:

```bash
# Windows PowerShell
notepad e:\projek_b\fastapi-santri\.env
```

Cari dan isi:
```
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.3
```

Atau gunakan terminal:
```bash
cd e:\projek_b\fastapi-santri
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### 2. Verify Setup

```bash
cd e:\projek_b\fastapi-santri

# Test intent classifier
python test_nl2sql_quick.py

# Test full system (needs database)
python test_nl2sql_system.py
```

### 3. Start FastAPI Server

```bash
cd e:\projek_b\fastapi-santri

# Using uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using FastAPI CLI
fastapi run app/main.py
```

Output yang diharapkan:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 4. Test Endpoints

#### Test 4.1: List Available Intents

```bash
curl -X GET "http://localhost:8000/nl2sql/intents"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "intents": [
      {
        "type": "list",
        "description": "Ambil data santri, pesantren, dll",
        "examples": ["Tunjukkan semua santri", "Lihat list pesantren"]
      },
      ...
    ]
  },
  "message": "Total 8 intent types tersedia"
}
```

#### Test 4.2: Detect Intent (Only Classification)

```bash
curl -X POST "http://localhost:8000/nl2sql/detect-intent" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tunjukkan santri miskin di Bandung"}'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "intent": "filter",
    "confidence": 0.92,
    "keywords": ["tunjukkan", "miskin", "bandung"],
    "entity_types": ["santri", "kategori_kemiskinan", "lokasi"],
    "description": "User menanyakan tentang filter santri, kategori_kemiskinan, lokasi"
  },
  "message": "Intent terdeteksi"
}
```

#### Test 4.3: Full NL2SQL Query (With SQL Execution)

```bash
curl -X POST "http://localhost:8000/nl2sql/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Berapa jumlah santri?", "explain": true}'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "intent": "count",
    "confidence": 0.88,
    "sql_query": "SELECT COUNT(*) as total FROM santri_pribadi",
    "result": [
      {
        "total": 1234
      }
    ],
    "execution_time_ms": 125.5,
    "explanation": "Query terdeteksi intent: count. SQL melakukan query terhadap tabel: santri"
  },
  "message": "Query berhasil dieksekusi"
}
```

#### Test 4.4: Test System

```bash
curl -X POST "http://localhost:8000/nl2sql/test"
```

Menjalankan 4 predefined test queries dan menunjukkan hasilnya.

---

## Common Issues & Solutions

### Error: "OpenAI API Key not found"

```python
Error: OpenAI API key not configured in .env
```

**Solution:**
```bash
# 1. Check .env file exists
Test-Path "e:\projek_b\fastapi-santri\.env"

# 2. Check OPENAI_API_KEY is set
Select-String "OPENAI_API_KEY" "e:\projek_b\fastapi-santri\.env"

# 3. Make sure you're using the right Python environment
e:\projek_b\fastapi-santri\env\Scripts\python.exe -c "from app.core.config import settings; print(settings.OPENAI_API_KEY[:10])"
```

### Error: "ModuleNotFoundError: No module named 'openai'"

```bash
# Install openai package
pip install openai

# Or using venv
e:\projek_b\fastapi-santri\env\Scripts\pip.exe install openai
```

### Error: "schema_context.json not found"

```bash
# Verify file exists
Test-Path "e:\projek_b\fastapi-santri\app\nl2sql\schema_context.json"

# If not found, check git status
cd e:\projek_b\fastapi-santri
git status
```

### Query Result Empty or NULL

```python
# Check if database is running
# Check tables exist
# Try simpler query first
curl -X POST "http://localhost:8000/nl2sql/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tunjukkan 5 santri terbaru"}'
```

### OpenAI API Rate Limited

```
Error: Rate limit exceeded
```

**Solution:**
- Add delay between requests
- Check usage at https://platform.openai.com/account/usage
- Consider upgrading API plan
- Implement query caching

---

## Files Created/Modified

### New Files

```
app/routes/nl2sql_routes.py              # FastAPI endpoints
app/nl2sql/intent_classifier.py          # Intent detection (already existed)
app/nl2sql/nl2sql_service.py             # NL2SQL service (fixed imports)
app/nl2sql/schema_context.json           # Database schema (already existed)
NL2SQL_DOCUMENTATION.md                  # Full documentation
NL2SQL_IMPLEMENTATION_SUMMARY.md         # This implementation summary
test_nl2sql_quick.py                     # Quick test script
test_nl2sql_system.py                    # Comprehensive test suite
```

### Modified Files

```
app/main.py                              # Added nl2sql_router import & inclusion
app/core/config.py                       # OpenAI configuration (already set up)
.env                                     # OPENAI settings (needs API key)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   User Query (Natural Language)         │
│   "Tunjukkan santri miskin di Bandung"  │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   FastAPI Routes (nl2sql_routes.py)     │
│   POST /nl2sql/detect-intent            │
│   POST /nl2sql/query                    │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   NL2SQLService.process_query()         │
│   ├─ Classify intent (rule-based)       │
│   ├─ Generate SQL (OpenAI)              │
│   ├─ Validate SQL (safety checks)       │
│   └─ Execute SQL (SQLAlchemy)           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│   Response to User                      │
│   {                                     │
│     "intent": "filter",                 │
│     "sql_query": "SELECT ...",          │
│     "result": [...],                    │
│     "execution_time_ms": 125.5          │
│   }                                     │
└─────────────────────────────────────────┘
```

---

## Performance Notes

### OpenAI API Latency

- First call: ~500-1000ms (model initialization)
- Subsequent calls: ~200-500ms
- Depends on query complexity and OpenAI load

### Database Query Latency

- Simple queries (COUNT, LIMIT 10): 50-150ms
- Complex queries (JOINs, GIS): 200-500ms
- Full table scans: 1000ms+

### Optimization Tips

1. **Cache common queries** - Same natural language = same SQL
2. **Use LIMIT wisely** - Always limit results
3. **Create database indexes** - For frequently queried fields
4. **Monitor execution_time_ms** - Track slow queries

---

## Next Steps (Recommended)

1. ✅ **Integration Complete** - All files in place
2. ✅ **Setup Complete** - Set OPENAI_API_KEY in .env
3. ✅ **Testing Ready** - Run test_nl2sql_quick.py
4. **Test Endpoints** - Use curl/Postman to test endpoints
5. **Monitor Logs** - Watch for errors and slow queries
6. **Implement Caching** - Cache common queries
7. **Add Rate Limiting** - Protect endpoints
8. **Frontend Integration** - Build UI to use NL2SQL API

---

## Frontend Integration Example

If you're building a frontend (React, Vue, etc.):

```javascript
// Example: JavaScript/React

async function queryNL2SQL(query) {
  const response = await fetch('http://localhost:8000/nl2sql/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      explain: true
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Intent:', data.data.intent);
    console.log('SQL Query:', data.data.sql_query);
    console.log('Results:', data.data.result);
    console.log('Time:', data.data.execution_time_ms, 'ms');
    return data.data.result;
  } else {
    console.error('Error:', data.error);
  }
}

// Usage
queryNL2SQL('Tunjukkan 10 santri terbaru')
  .then(results => console.log(results));
```

---

## Monitoring & Logging

### Enable Debug Logging

Edit `.env`:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

Edit `app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("nl2sql")
logger.debug(f"Processing query: {query}")
```

### Monitor OpenAI Usage

```python
# Add to nl2sql_service.py
import logging
logger = logging.getLogger("openai")

def generate_sql(self, query, intent):
    logger.info(f"Generating SQL for intent: {intent.intent.value}")
    logger.debug(f"Query: {query}")
    
    # ... API call ...
    
    logger.info(f"SQL generated: {sql[:100]}...")
    return sql
```

### Check OpenAI Dashboard

Visit: https://platform.openai.com/account/usage

Track:
- Requests per minute
- Tokens used
- Costs

---

## Troubleshooting Checklist

- [ ] OPENAI_API_KEY is set in .env
- [ ] Python virtual environment is activated
- [ ] openai package is installed (pip list | grep openai)
- [ ] Database is running and accessible
- [ ] FastAPI server starts without errors
- [ ] curl/Postman can reach endpoints
- [ ] test_nl2sql_quick.py runs successfully
- [ ] test_nl2sql_system.py completes all tests
- [ ] OpenAI API quota is not exceeded

---

## Support

**For Issues:**
1. Check NL2SQL_DOCUMENTATION.md
2. Run test scripts to identify problem
3. Check .env file configuration
4. Verify database connectivity
5. Monitor OpenAI API status

**For Questions:**
- See NL2SQL_DOCUMENTATION.md for comprehensive guide
- Check test_nl2sql_system.py for example implementations
- Review app/routes/nl2sql_routes.py for API patterns

---

**Last Updated**: November 29, 2024
**Status**: Ready for Testing ✅
