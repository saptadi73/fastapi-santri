from app.core.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    # Delete records with invalid enum values
    conn.execute(text("DELETE FROM pesantren_fasilitas WHERE asrama = 'cukup_lengkap'"))
    print("✓ Deleted records with invalid asrama='cukup_lengkap'")
    
    # Check remaining records
    result = conn.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas"))
    count = result.scalar()
    print(f"✓ Remaining records in pesantren_fasilitas: {count}")
