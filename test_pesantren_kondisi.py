"""
Debug query pesantren dengan kondisi spesifik
"""
import requests
import json

BASE_URL = "http://localhost:8000"

query = "berikan 10 pesantren dengan kondisi air berbau dan fasilitas mck tidak layak di Jakarta"

print("=" * 80)
print(f"Testing Query: {query}")
print("=" * 80)

try:
    response = requests.post(
        f"{BASE_URL}/nl2sql/query",
        json={"query": query},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    data = response.json()
    
    if data.get('success'):
        result_data = data.get('data', {})
        sql = result_data.get('sql_query', '')
        
        print("SQL Query:")
        print(sql)
        print()
        
        results = result_data.get('result', [])
        print(f"Results: {len(results) if isinstance(results, list) else 'N/A'} rows")
        
        if isinstance(results, list) and len(results) > 0:
            print("\nSample data:")
            print(json.dumps(results[0], indent=2, default=str))
        elif isinstance(results, list) and len(results) == 0:
            print("\n⚠️ Query berhasil tapi tidak ada data yang match")
        else:
            print(f"\nResult: {results}")
    else:
        print("Error Response:")
        print(json.dumps(data, indent=2, default=str))
    
except Exception as e:
    print(f"Exception: {str(e)}")
    import traceback
    traceback.print_exc()
