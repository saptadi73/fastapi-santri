"""Quick test untuk lihat response dari API"""
import requests
import json

response = requests.post(
    "http://localhost:8000/nl2sql/query",
    json={"query": "berikan 10 santri score tertinggi"},
    timeout=10
)

print("Status:", response.status_code)
print("\nResponse:")
data = response.json()
print(json.dumps(data, indent=2, default=str)[:1000])
