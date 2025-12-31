"""Fix all invalid enum values in database."""
from app.core.database import SessionLocal, engine
from sqlalchemy import text

# Use engine.begin() for atomic transaction
with engine.begin() as conn:
    # Fix asrama - 'cukup_lengkap' is not valid
    # Valid values: layak, cukup, tidak_layak
    result = conn.execute(text("UPDATE pesantren_fasilitas SET asrama = 'cukup' WHERE asrama = 'cukup_lengkap'"))
    print(f"✓ Fixed asrama: {result.rowcount} rows updated")
    
    # Fix fasilitas_transportasi - 'cukup_lengkap' is not valid
    # Valid values: bus, angkutan_umum, kendaraan_pribadi, ojek
    result = conn.execute(text("UPDATE pesantren_fasilitas SET fasilitas_transportasi = 'angkutan_umum' WHERE fasilitas_transportasi = 'cukup_lengkap'"))
    print(f"✓ Fixed fasilitas_transportasi: {result.rowcount} rows updated")
    
    # Fix akses_jalan - 'baik' is not valid
    # Valid values: aspal, cor_block, tanah, kerikil
    result = conn.execute(text("UPDATE pesantren_fasilitas SET akses_jalan = 'aspal' WHERE akses_jalan = 'baik'"))
    print(f"✓ Fixed akses_jalan: {result.rowcount} rows updated")

# Verify
db = SessionLocal()
result = db.execute(text('SELECT id, asrama, ruang_belajar, fasilitas_transportasi, akses_jalan FROM pesantren_fasilitas'))
rows = list(result)
print('\nVerification:')
for r in rows:
    print(f'  asrama: {r[1]}, ruang_belajar: {r[2]}, fasilitas_transportasi: {r[3]}, akses_jalan: {r[4]}')
db.close()
