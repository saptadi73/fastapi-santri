"""
Test NL2SQL dengan query pesantren
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("TEST PESANTREN QUERY dengan JOIN")
print("=" * 80)

test_queries = [
    "Berikan 5 pesantren dengan skor tertinggi",
    "Tampilkan pesantren di Jawa Barat dengan skor di atas 150",
    "Santri miskin beserta nama pesantrennya di Bandung"
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('-' * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/nl2sql/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_data = data.get('data', {})
                sql = result_data.get('sql_query', '')
                
                print(f"✅ Query berhasil")
                print(f"\nSQL Generated:")
                print(f"{sql}\n")
                
                # Check if JOIN is used
                if 'JOIN' in sql.upper():
                    print("✅ Menggunakan JOIN")
                else:
                    print("⚠️  Tidak menggunakan JOIN")
                
                results = result_data.get('result', [])
                if isinstance(results, list) and len(results) > 0:
                    print(f"\nHasil: {len(results)} rows")
                    print(f"Kolom: {list(results[0].keys())}")
                    print(f"\nSample data (row 1):")
                    print(json.dumps(results[0], indent=2, default=str))
                else:
                    print(f"Hasil: {results}")
            else:
                print(f"❌ Error: {data.get('error', 'Unknown')}")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 80)
