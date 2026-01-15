"""Test santri queries masih punya koordinat"""
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
    
    data = response.json()
    
    if response.status_code == 200:
        response_data = data.get('data', {})
        results = response_data.get('result', [])
        
        if isinstance(results, list) and results:
            first = results[0]
            if 'latitude' in first and 'longitude' in first:
                print(f"✅ KOORDINAT OK! ({first['latitude']}, {first['longitude']})")
            else:
                print(f"❌ KOORDINAT HILANG! Keys: {list(first.keys())}")
        else:
            print(f"⚠️ No results")
    else:
        print(f"❌ Error: {data}")

if __name__ == "__main__":
    test_query("Berikan 10 santri score tertinggi")
    test_query("Santri miskin di Bandung")
    test_query("Berapa jumlah santri per kategori kemiskinan")
