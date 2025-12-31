"""Test script for Map GIS functionality."""
import sys
sys.path.insert(0, 'e:/projek_b/fastapi-santri')

from app.main import app  # Load all models
from app.core.database import SessionLocal
from app.services.santri_map_service import SantriMapService
from app.services.pesantren_map_service import PesantrenMapService
import json

print("=== Testing Map GIS Services ===\n")

db = SessionLocal()

# Initialize services
santri_service = SantriMapService(db)
pesantren_service = PesantrenMapService(db)

# Test Santri Map Statistics
print("1. Testing Santri Map Statistics:")
try:
    stats = santri_service.get_statistics()
    print(json.dumps(stats, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test Pesantren Map Statistics
print("2. Testing Pesantren Map Statistics:")
try:
    stats = pesantren_service.get_statistics()
    print(json.dumps(stats, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test Santri GeoJSON (first 5)
print("3. Testing Santri GeoJSON (limit 5):")
try:
    geojson = santri_service.get_all_geojson(limit=5)
    print(f"Total features: {geojson['total']}")
    if geojson['features']:
        print(f"First feature properties:")
        print(json.dumps(geojson['features'][0]['properties'], indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test Pesantren GeoJSON (first 5)
print("4. Testing Pesantren GeoJSON (limit 5):")
try:
    geojson = pesantren_service.get_all_geojson(limit=5)
    print(f"Total features: {geojson['total']}")
    if geojson['features']:
        print(f"First feature properties:")
        print(json.dumps(geojson['features'][0]['properties'], indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")

db.close()
print("\n✅ Test completed!")
