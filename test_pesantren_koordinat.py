"""Test pesantren query dengan koordinat untuk peta"""
import requests

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
        print(f"\n✅ Success!")
        print(f"Intent: {data.get('intent')}")
        print(f"SQL: {data.get('sql')}")
        print(f"\nResults count: {len(data.get('results', []))}")
        
        # Show first few results
        results = data.get('results', [])
        if results:
            print(f"\nFirst result:")
            first = results[0]
            for key, value in first.items():
                print(f"  {key}: {value}")
            
            # Check for coordinates
            if 'latitude' in first and 'longitude' in first:
                print(f"\n✅ KOORDINAT DITEMUKAN!")
                print(f"   Latitude: {first['latitude']}")
                print(f"   Longitude: {first['longitude']}")
            else:
                print(f"\n❌ KOORDINAT TIDAK ADA!")
                print(f"   Keys available: {list(first.keys())}")
        else:
            print("\n⚠️ No results returned")
    else:
        print(f"\n❌ Error: {data}")

if __name__ == "__main__":
    # Test 1: Simple pesantren query with high score
    test_query("Berikan 5 pesantren dengan skor tertinggi")
    
    # Test 2: Pesantren in specific province
    test_query("Pesantren di Jawa Barat")
    
    # Test 3: Pesantren with conditions
    test_query("Pesantren skor tinggi di Jakarta")
