"""
Simple NL2SQL Query Test with longer timeout
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TESTING NL2SQL QUERY ENDPOINT")
print("=" * 80)

# Test queries
test_queries = [
    "Tunjukkan 10 santri terbaru",
    "Berapa jumlah santri di Jawa Barat?",
    "Pesantren dengan skor tertinggi"
]

for query in test_queries:
    print(f"\n[Query] {query}")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/nl2sql/query",
            json={"query": query, "explain": False},
            timeout=60  # 60 second timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_data = data.get('data', {})
                print(f"✅ Success!")
                print(f"   Intent: {result_data.get('intent', 'N/A')}")
                print(f"   SQL: {result_data.get('sql_query', 'N/A')[:100]}...")
                print(f"   Execution time: {result_data.get('execution_time_ms', 'N/A')} ms")
                
                # Show results count
                results = result_data.get('result', [])
                if isinstance(results, list):
                    print(f"   Results: {len(results)} rows")
                    if len(results) > 0:
                        print(f"   First result: {json.dumps(results[0], indent=2)[:200]}...")
            else:
                print(f"❌ Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out (>60s)")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)
