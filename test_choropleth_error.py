"""Quick test to see actual error from endpoint"""
import requests

response = requests.get("http://127.0.0.1:8000/gis/choropleth/santri-kabupaten")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
