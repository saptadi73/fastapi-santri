import requests
import json

pesantren_id = "bfc0e58b-de57-4f22-84e3-5c36cd2002de"
url = f"http://127.0.0.1:8000/pesantren-fasilitas/pesantren/{pesantren_id}"

response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2))
