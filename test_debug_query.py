"""
Debug query yang error 400
"""
import requests
import json

BASE_URL = "http://localhost:8000"

query = "berikan kabupaten score urutan tertinggi di Jawa Tengah"

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
    print("Response:")
    print(json.dumps(data, indent=2, default=str))
    
    if data.get('data'):
        result_data = data.get('data', {})
        if 'sql_query' in result_data:
            print(f"\nSQL Query:")
            print(result_data['sql_query'])
        if 'error' in result_data:
            print(f"\nError:")
            print(result_data['error'])
    
except Exception as e:
    print(f"Exception: {str(e)}")
    import traceback
    traceback.print_exc()
