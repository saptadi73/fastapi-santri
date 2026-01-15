"""
Test NL2SQL Query dengan Result Enrichment
Memastikan response menampilkan detail lengkap, bukan hanya ID
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("NL2SQL QUERY TEST - RESULT ENRICHMENT")
print("=" * 80)

# Test queries
test_queries = [
    {
        "query": "berikan 10 santri score tertinggi",
        "description": "Top 10 santri dengan score tertinggi",
        "expected_fields": ["santri_id", "skor_total", "nama_santri", "alamat"]
    },
    {
        "query": "tampilkan santri miskin dengan skor di atas 100",
        "description": "Santri miskin dengan score > 100",
        "expected_fields": ["santri_id", "skor_total", "nama_santri", "kategori_kemiskinan"]
    },
    {
        "query": "berapa santri di kategori sangat miskin",
        "description": "Count santri kategori sangat miskin",
        "expected_fields": ["count", "kategori_kemiskinan"]
    }
]

def test_query(query_text: str, description: str, expected_fields: list):
    """Test sebuah query."""
    print(f"\n[Test] {description}")
    print(f"Query: {query_text}")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/nl2sql/query",
            json={"query": query_text, "explain": False},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_data = data.get('data', {})
                print(f"✅ Query executed successfully")
                print(f"   Intent: {result_data.get('intent', 'N/A')}")
                print(f"   SQL: {result_data.get('sql_query', 'N/A')[:100]}...")
                print(f"   Execution time: {result_data.get('execution_time_ms', 'N/A')}ms")
                
                results = result_data.get('result', [])
                if isinstance(results, list) and len(results) > 0:
                    print(f"   Results: {len(results)} rows")
                    
                    # Show columns available
                    first_row = results[0]
                    actual_fields = list(first_row.keys())
                    print(f"   Available columns: {actual_fields}")
                    
                    # Check expected fields
                    found_fields = [f for f in expected_fields if f in actual_fields]
                    missing_fields = [f for f in expected_fields if f not in actual_fields]
                    
                    if found_fields:
                        print(f"   ✅ Found expected fields: {found_fields}")
                    if missing_fields:
                        print(f"   ⚠️  Missing expected fields: {missing_fields}")
                    
                    # Show sample data
                    print(f"\n   Sample row:")
                    for key, value in list(first_row.items())[:5]:
                        print(f"     {key}: {value}")
                    if len(first_row) > 5:
                        print(f"     ... and {len(first_row) - 5} more fields")
                
                elif isinstance(results, dict):
                    print(f"   Result type: dict")
                    print(f"   Keys: {list(results.keys())[:10]}")
                    
            else:
                error = data.get('error', 'Unknown error')
                print(f"❌ Query failed: {error}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out (>30s)")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

# Wait for server
print("\nWaiting for server to be ready...")
import time
for i in range(5):
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            print(f"✅ Server ready on {BASE_URL}\n")
            break
    except:
        pass
    time.sleep(1)
else:
    print(f"❌ Server not responding on {BASE_URL}")
    print("Make sure server is running: python -m uvicorn app.main:app --reload")
    sys.exit(1)

# Run tests
for test_case in test_queries:
    test_query(
        test_case["query"],
        test_case["description"],
        test_case["expected_fields"]
    )

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
