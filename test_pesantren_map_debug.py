"""Debug script for Pesantren Map GIS."""
import sys
sys.path.insert(0, 'e:/projek_b/fastapi-santri')

from app.main import app
from app.core.database import SessionLocal
from app.services.pesantren_map_service import PesantrenMapService
from app.models.pesantren_map import PesantrenMap
import json

db = SessionLocal()

print("=" * 60)
print("PESANTREN MAP GIS DEBUG")
print("=" * 60)

# Test 1: Check database records
print("\n1️⃣ Checking pesantren_map table:")
try:
    records = db.query(PesantrenMap).all()
    print(f"   Total records: {len(records)}")
    for record in records:
        print(f"   - ID: {record.id}")
        print(f"     Nama: {record.nama}")
        print(f"     Skor: {record.skor_terakhir}")
        print(f"     Kategori: {record.kategori_kelayakan}")
        print(f"     Lokasi: {record.lokasi}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test GeoJSON service
print("\n2️⃣ Testing get_all_geojson():")
try:
    service = PesantrenMapService(db)
    geojson = service.get_all_geojson(limit=10)
    print(f"   ✅ Success")
    print(f"   Type: {geojson['type']}")
    print(f"   Features count: {len(geojson['features'])}")
    print(f"   Total: {geojson.get('total', 'N/A')}")
    
    if geojson['features']:
        print(f"\n   First feature:")
        feature = geojson['features'][0]
        print(f"     - Geometry type: {feature['geometry']['type']}")
        print(f"     - Coordinates: {feature['geometry']['coordinates']}")
        print(f"     - Properties: {json.dumps(feature['properties'], indent=8, default=str)}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test with filters
print("\n3️⃣ Testing with kategori filter:")
try:
    service = PesantrenMapService(db)
    geojson = service.get_all_geojson(kategori="sangat_layak", limit=10)
    print(f"   ✅ Success")
    print(f"   Features count: {len(geojson['features'])}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

# Test 4: Test bounding box
print("\n4️⃣ Testing get_by_bounding_box():")
try:
    service = PesantrenMapService(db)
    records = service.get_by_bounding_box(
        min_lon=106.8,
        min_lat=-6.3,
        max_lon=106.9,
        max_lat=-6.2
    )
    print(f"   ✅ Success")
    print(f"   Records found: {len(records)}")
    for record in records:
        print(f"     - {record.nama} ({record.skor_terakhir})")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test statistics
print("\n5️⃣ Testing get_statistics():")
try:
    service = PesantrenMapService(db)
    stats = service.get_statistics()
    print(f"   ✅ Success")
    print(f"   Statistics: {json.dumps(stats, indent=2, default=str)}")
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")

db.close()
print("\n" + "=" * 60)
print("✅ Debug completed!")
print("=" * 60)
