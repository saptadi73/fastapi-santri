"""
Check actual values di pesantren_fisik
"""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 80)
print("CHECKING ACTUAL VALUES IN pesantren_fisik")
print("=" * 80)

# Check distinct values untuk kualitas_air_bersih
print("\n1. kualitas_air_bersih values:")
query = "SELECT DISTINCT kualitas_air_bersih FROM pesantren_fisik ORDER BY kualitas_air_bersih LIMIT 20"
results = db.execute(text(query)).fetchall()
for row in results:
    print(f"   - {row[0]}")

# Check distinct values untuk fasilitas_mck
print("\n2. fasilitas_mck values:")
query = "SELECT DISTINCT fasilitas_mck FROM pesantren_fisik ORDER BY fasilitas_mck LIMIT 20"
results = db.execute(text(query)).fetchall()
for row in results:
    print(f"   - {row[0]}")

# Check kabupaten values
print("\n3. kabupaten values (sample):")
query = "SELECT DISTINCT kabupaten FROM pondok_pesantren ORDER BY kabupaten LIMIT 30"
results = db.execute(text(query)).fetchall()
for row in results:
    print(f"   - {row[0]}")

# Check if any pesantren with bad water/mck exists
print("\n4. Pesantren dengan kondisi air/mck buruk (any location):")
query = """
SELECT pp.nama, pp.kabupaten, pf.kualitas_air_bersih, pf.fasilitas_mck 
FROM pondok_pesantren pp 
JOIN pesantren_fisik pf ON pp.id = pf.pesantren_id 
WHERE pf.kualitas_air_bersih ILIKE '%bau%' OR pf.fasilitas_mck ILIKE '%tidak%'
LIMIT 5
"""
results = db.execute(text(query)).fetchall()
for row in results:
    print(f"   - {row[0]} ({row[1]}): air={row[2]}, mck={row[3]}")

db.close()
