"""Test pesantren query dengan koordinat untuk peta - debug version"""
import requests
import json

API_URL = "http://localhost:8000/nl2sql/query"

def test_query(query):
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    response = requests.post(
        API_URL,
        json={"query": query}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        response_data = data.get('data', {})
        print(f"✅ Success!")
        print(f"SQL: {response_data.get('sql_query')[:100]}...")
        
        results = response_data.get('result', [])
        print(f"Results count: {len(results) if isinstance(results, list) else 'N/A'}")
        
        # Show first few results
        if isinstance(results, list) and results:
            first = results[0]
            
            # Check for coordinates
            if 'latitude' in first and 'longitude' in first:
                print(f"✅ KOORDINAT DITEMUKAN!")
                print(f"   First: {first.get('nama')} @ ({first['latitude']}, {first['longitude']})")
            else:
                print(f"❌ KOORDINAT TIDAK ADA!")
                print(f"   Keys: {list(first.keys())}")
    else:
        print(f"❌ Error: {data}")

if __name__ == "__main__":
    # Test 1: Pesantren with highest score
    test_query("Berikan 5 pesantren dengan skor tertinggi")
    
    # Test 2: Pesantren in specific province
    test_query("Pesantren di Jawa Barat")
    
    # Test 3: Pesantren in specific city
    test_query("Pesantren skor tinggi di Bandung")
    
    # Test 4: Aggregate query (should NOT have coordinates)
    test_query("Berapa jumlah pesantren per kabupaten di Jawa Barat")

