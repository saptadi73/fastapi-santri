"""
Test NL2SQL API Endpoints
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_endpoint(endpoint, method="GET", data=None, name=""):
    """Test API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        return {
            "success": response.status_code in [200, 201],
            "status": response.status_code,
            "data": response.json() if response.text else None
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "status": None, "error": "Connection refused"}
    except Exception as e:
        return {"success": False, "status": None, "error": str(e)}

print("=" * 80)
print("NL2SQL API ENDPOINT TESTS")
print("=" * 80)

# Wait for server to be ready
print("\nWaiting for server to be ready...")
for i in range(5):
    result = test_endpoint("/api/health")
    if result['success']:
        print(f"✅ Server ready on {BASE_URL}")
        break
    time.sleep(1)
else:
    print(f"❌ Server not responding on {BASE_URL}")
    print("Make sure server is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
    exit(1)

# Test 1: Health Check
print("\n[1] Health Check")
print("-" * 80)
result = test_endpoint("/api/health")
if result['success']:
    print(f"✅ API is healthy")
    print(f"   Status: {result['data']}")
else:
    print(f"❌ Health check failed: {result.get('error', result['status'])}")

# Test 2: NL2SQL Intent Detection
print("\n[2] Intent Detection Endpoint (/nl2sql/intent)")
print("-" * 80)

test_queries = [
    "Tunjukkan semua santri di Bandung",
    "Berapa jumlah santri miskin?",
    "Top 10 pesantren dengan skor tertinggi",
    "Santri di kategori sangat miskin",
]

for query in test_queries:
    result = test_endpoint("/nl2sql/intent", method="POST", data={"query": query})
    if result['success']:
        data = result['data']
        print(f"✅ Query: '{query[:40]}...'")
        print(f"   Intent: {data.get('intent', 'N/A')}")
        print(f"   Confidence: {data.get('confidence', 0):.2f}")
    else:
        print(f"❌ Query: '{query[:40]}...'")
        print(f"   Error: {result.get('error', 'Unknown')}")

# Test 3: SQL Validation
print("\n[3] SQL Validation Endpoint (/nl2sql/validate-sql)")
print("-" * 80)

test_sqls = [
    ("SELECT * FROM santri LIMIT 100", True),
    ("DELETE FROM santri", False),
    ("SELECT * FROM pesantren", False),
]

for sql, should_pass in test_sqls:
    result = test_endpoint("/nl2sql/validate-sql", method="POST", data={"sql": sql})
    if result['success']:
        is_valid = result['data'].get('is_valid', False)
        status = "✅" if is_valid == should_pass else "⚠️"
        print(f"{status} SQL: '{sql[:35]}...'")
        if not is_valid:
            print(f"   Error: {result['data'].get('error', 'None')}")
    else:
        print(f"❌ SQL: '{sql[:35]}...'")
        print(f"   Error: {result.get('error', 'Unknown')}")

# Test 4: Schema Context
print("\n[4] Schema Context Endpoint (/nl2sql/schema)")
print("-" * 80)

result = test_endpoint("/nl2sql/schema", method="GET")
if result['success']:
    schema = result['data']
    print(f"✅ Schema loaded")
    print(f"   Database: {schema.get('database', 'N/A')}")
    print(f"   Tables: {len(schema.get('tables', {}))}")
    tables = list(schema.get('tables', {}).keys())
    print(f"   Sample tables: {tables[:3]}")
else:
    print(f"❌ Schema error: {result.get('error', 'Unknown')}")

# Test 5: Test Endpoint
print("\n[5] Test Endpoint (/nl2sql/test)")
print("-" * 80)

result = test_endpoint("/nl2sql/test", method="POST", data={})
if result['success']:
    print(f"✅ Test endpoint working")
    data = result['data']
    if isinstance(data, list):
        print(f"   Test cases executed: {len(data)}")
        if data:
            print(f"   Sample result: {data[0]}")
    else:
        print(f"   Response: {str(data)[:100]}...")
else:
    print(f"❌ Test endpoint error: {result.get('error', 'Unknown')}")

print("\n" + "=" * 80)
print("API ENDPOINT TESTS COMPLETED")
print("=" * 80)
