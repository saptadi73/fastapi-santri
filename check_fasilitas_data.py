from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check all data in pesantren_fasilitas
result = db.execute(text("""
    SELECT 
        id, 
        asrama,
        ruang_belajar,
        internet,
        fasilitas_transportasi,
        akses_jalan
    FROM pesantren_fasilitas
"""))

print("=== All records in pesantren_fasilitas ===")
rows = result.fetchall()
if not rows:
    print("No records found")
else:
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"  asrama: {row[1]}")
        print(f"  ruang_belajar: {row[2]}")
        print(f"  internet: {row[3]}")
        print(f"  fasilitas_transportasi: {row[4]}")
        print(f"  akses_jalan: {row[5]}")
        print()
