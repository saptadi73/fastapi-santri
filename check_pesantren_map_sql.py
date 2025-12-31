from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check records in pesantren_map using raw SQL
result = db.execute(text("SELECT COUNT(*) as cnt FROM pesantren_map")).fetchone()
count = result[0] if result else 0
print(f"✅ Records in pesantren_map: {count}")

if count > 0:
    result = db.execute(text("""
        SELECT nama, skor_terakhir, kategori_kelayakan 
        FROM pesantren_map
    """)).fetchall()
    for row in result:
        print(f"  - {row[0]}: Score {row[1]} ({row[2]})")
else:
    print("⚠️ No records found in pesantren_map")
    
    # Check if there are any pesantren in pondok_pesantren table
    result = db.execute(text("SELECT COUNT(*) as cnt FROM pondok_pesantren")).fetchone()
    pesantren_count = result[0] if result else 0
    print(f"\nℹ️ Total pesantren in database: {pesantren_count}")
    
    if pesantren_count > 0:
        # Get one pesantren ID
        result = db.execute(text("SELECT id, nama FROM pondok_pesantren LIMIT 1")).fetchone()
        if result:
            pesantren_id = result[0]
            pesantren_nama = result[1]
            print(f"ℹ️ Sample pesantren: {pesantren_nama}")
            print(f"   ID: {pesantren_id}")
            print(f"\n💡 To test pesantren_map auto-update:")
            print(f"   POST http://127.0.0.1:8000/api/pesantren-scoring/{pesantren_id}/calculate")
            
            # Check if pesantren has fisik, fasilitas, pendidikan data
            result = db.execute(text("SELECT COUNT(*) FROM pesantren_fisik WHERE pesantren_id = :id"), {"id": pesantren_id}).fetchone()
            fisik_count = result[0] if result else 0
            result = db.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas WHERE pesantren_id = :id"), {"id": pesantren_id}).fetchone()
            fasilitas_count = result[0] if result else 0
            result = db.execute(text("SELECT COUNT(*) FROM pesantren_pendidikan WHERE pesantren_id = :id"), {"id": pesantren_id}).fetchone()
            pendidikan_count = result[0] if result else 0
            
            print(f"\n📊 Data status for {pesantren_nama}:")
            print(f"   - Fisik: {'✅' if fisik_count > 0 else '❌'} ({fisik_count} record)")
            print(f"   - Fasilitas: {'✅' if fasilitas_count > 0 else '❌'} ({fasilitas_count} record)")
            print(f"   - Pendidikan: {'✅' if pendidikan_count > 0 else '❌'} ({pendidikan_count} record)")

db.close()
