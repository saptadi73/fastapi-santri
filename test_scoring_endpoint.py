"""Test the pesantren scoring endpoint"""
import requests
import json

# Test the endpoint
pesantren_id = "ccbaa80e-9384-42fd-a45b-0157eef8fca9"
url = f"http://localhost:8000/api/pesantren-scoring/pesantren/{pesantren_id}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
