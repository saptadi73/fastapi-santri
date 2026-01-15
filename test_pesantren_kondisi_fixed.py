"""
Test query pesantren dengan kondisi buruk
"""
import requests
import json

BASE_URL = "http://localhost:8000"

test_queries = [
    "berikan 10 pesantren dengan kondisi air berbau dan fasilitas mck tidak layak",
    "pesantren di Jember dengan air berbau",
    "pesantren dengan mck tidak layak di Surabaya"
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
                
                print(f"SQL:\n{sql}\n")
                
                results = result_data.get('result', [])
                print(f"Results: {len(results) if isinstance(results, list) else 'N/A'} rows")
                
                if isinstance(results, list) and len(results) > 0:
                    print(f"\nSample:")
                    print(json.dumps(results[0], indent=2, default=str))
            else:
                print(f"Error: {data.get('message')}")
        else:
            print(f"HTTP {response.status_code}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print()
