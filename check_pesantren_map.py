from app.core.database import SessionLocal
from app.models.pesantren_map import PesantrenMap
from sqlalchemy import text

db = SessionLocal()

# Check records in pesantren_map
count = db.query(PesantrenMap).count()
print(f"✅ Records in pesantren_map: {count}")

if count > 0:
    maps = db.query(PesantrenMap).all()
    for m in maps:
        print(f"  - {m.nama}: Score {m.skor_terakhir} ({m.kategori_kelayakan})")
else:
    print("⚠️ No records found in pesantren_map")
    
    # Check if there are any pesantren in pondok_pesantren table
    result = db.execute(text("SELECT COUNT(*) as cnt FROM pondok_pesantren")).fetchone()
    pesantren_count = result[0]
    print(f"\nℹ️ Total pesantren in database: {pesantren_count}")
    
    if pesantren_count > 0:
        # Get one pesantren ID
        result = db.execute(text("SELECT id, nama FROM pondok_pesantren LIMIT 1")).fetchone()
        pesantren_id = result[0]
        pesantren_nama = result[1]
        print(f"ℹ️ Sample pesantren: {pesantren_nama} (ID: {pesantren_id})")
        print(f"\n💡 You need to calculate pesantren score first:")
        print(f"   POST http://127.0.0.1:8000/api/pesantren-scoring/{pesantren_id}/calculate")

db.close()
