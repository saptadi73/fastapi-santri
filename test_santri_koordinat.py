"""
Test query santri dengan koordinat untuk peta
"""
import requests
import json

BASE_URL = "http://localhost:8000"

test_queries = [
    "berikan 10 santri score tertinggi",
    "santri miskin di Bandung",
    "santri sangat miskin di Jawa Barat"
]

for query in test_queries:
    print("=" * 80)
    print(f"Query: {query}")
    print("-" * 80)
    
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
                
                # Check if SQL includes latitude and longitude
                has_lat = 'latitude' in sql.lower()
                has_lon = 'longitude' in sql.lower()
                
                print(f"SQL includes latitude: {'✅' if has_lat else '❌'}")
                print(f"SQL includes longitude: {'✅' if has_lon else '❌'}")
                print(f"\nSQL:\n{sql}\n")
                
                results = result_data.get('result', [])
                if isinstance(results, list) and len(results) > 0:
                    print(f"Results: {len(results)} rows")
                    
                    # Check if result has lat/long
                    first_row = results[0]
                    has_lat_result = 'latitude' in first_row
                    has_lon_result = 'longitude' in first_row
                    
                    print(f"Result has latitude: {'✅' if has_lat_result else '❌'}")
                    print(f"Result has longitude: {'✅' if has_lon_result else '❌'}")
                    
                    print(f"\nSample result columns: {list(first_row.keys())}")
                    
                    if has_lat_result and has_lon_result:
                        print(f"\n📍 Koordinat sample: lat={first_row['latitude']}, lon={first_row['longitude']}")
                else:
                    print(f"No results")
            else:
                print(f"Error: {data.get('message')}")
        else:
            print(f"HTTP {response.status_code}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print()
