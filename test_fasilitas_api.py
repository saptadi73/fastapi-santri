import requests
import json

url = "http://127.0.0.1:8000/pesantren-fasilitas"
headers = {"Content-Type": "application/json"}
data = {
    "pesantren_id": "bfc0e58b-de57-4f22-84e3-5c36cd2002de",
    "jumlah_kamar": 50,
    "asrama": "layak"
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
