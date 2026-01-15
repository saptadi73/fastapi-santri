"""
Direct API test untuk melihat response detail
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("DIRECT API TEST - FULL RESPONSE")
print("=" * 80)

query = "berikan 10 santri score tertinggi"
print(f"\nQuery: {query}\n")

try:
    response = requests.post(
        f"{BASE_URL}/nl2sql/query",
        json={"query": query, "explain": False},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFull Response:")
        print(json.dumps(data, indent=2, default=str)[:3000])
        
        if data.get('success'):
            result_data = data.get('data', {})
            results = result_data.get('result', [])
            if isinstance(results, list) and len(results) > 0:
                print(f"\n\nFirst Result Row (Full Details):")
                print(json.dumps(results[0], indent=2, default=str))
    else:
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
