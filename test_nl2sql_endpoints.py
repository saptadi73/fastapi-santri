"""
Test NL2SQL endpoints on the API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        return {
            "status": response.status_code,
            "success": response.status_code in [200, 201],
            "data": response.json() if response.text else None
        }
    except Exception as e:
        return {
            "status": None,
            "success": False,
            "error": str(e)
        }

print("=" * 80)
print("TESTING NL2SQL ENDPOINTS ON FASTAPI SERVER")
print("=" * 80)

# Test 1: Health check
print("\n[1] Health Check")
print("-" * 80)
result = test_endpoint("/")
if result['success']:
    print(f"✅ Server is running: {result['data']}")
else:
    print(f"❌ Server not available: {result.get('error', 'Connection failed')}")
    print("\n⚠️  Make sure FastAPI server is running on http://localhost:8000")
    exit(1)

# Test 2: NL2SQL test endpoint (basic test)
print("\n[2] NL2SQL Test Endpoint")
print("-" * 80)
result = test_endpoint("/nl2sql/test", method="POST")
if result['success']:
    print(f"✅ NL2SQL test endpoint working")
    print(f"Response: {json.dumps(result['data'], indent=2)[:500]}...")
else:
    print(f"⚠️  Response status: {result['status']}")
    if result.get('data'):
        print(f"Response: {json.dumps(result['data'], indent=2)[:500]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

# Test 3: Intent detection endpoint
print("\n[3] Intent Detection Endpoint")
print("-" * 80)
test_queries = [
    "Tunjukkan semua santri",
    "Berapa jumlah santri di Jawa Barat",
    "Pesantren dengan skor tertinggi",
    "Santri miskin di kategori Sangat Miskin"
]

for query in test_queries:
    result = test_endpoint("/nl2sql/detect-intent", method="POST", data={"query": query})
    if result['success']:
        intent_data = result['data'].get('data', {})
        print(f"  Query: '{query}'")
        print(f"    Intent: {intent_data.get('intent', 'N/A')}")
        confidence = intent_data.get('confidence', 0)
        if isinstance(confidence, (int, float)):
            print(f"    Confidence: {confidence:.2f}")
        else:
            print(f"    Confidence: {confidence}")
    else:
        print(f"  Query: '{query}'")
        print(f"    ❌ Error: {result.get('error', 'Unknown')}")

# Test 4: Schema context endpoint
print("\n[4] Schema Context Endpoint")
print("-" * 80)
result = test_endpoint("/nl2sql/map/schema", method="GET")
if result['success']:
    schema_data = result['data']
    if 'tables' in schema_data:
        print(f"✅ Schema loaded successfully")
        print(f"   Tables available: {len(schema_data['tables'])}")
        print(f"   First few tables: {list(schema_data['tables'].keys())[:3]}")
    else:
        print(f"Response: {json.dumps(schema_data, indent=2)[:300]}...")
else:
    print(f"⚠️  Response status: {result['status']}")
    print(f"Error: {result.get('error', 'Unknown error')}")

# Test 5: List Available Intents
print("\n[5] List Available Intents")
print("-" * 80)
result = test_endpoint("/nl2sql/intents", method="GET")
if result['success']:
    intents = result['data'].get('data', {}).get('intents', [])
    print(f"✅ Found {len(intents)} intent types:")
    for intent in intents[:5]:  # Show first 5
        print(f"   - {intent.get('type')}: {intent.get('description', 'N/A')[:50]}...")
else:
    print(f"⚠️  Response status: {result['status']}")
    print(f"Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
