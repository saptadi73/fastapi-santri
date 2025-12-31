from app.core.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    # Delete all records with invalid enum values
    conn.execute(text("DELETE FROM pesantren_fasilitas"))
    print("✓ Deleted all pesantren_fasilitas records")
    
    # Check remaining records
    result = conn.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas"))
    count = result.scalar()
    print(f"✓ Remaining records: {count}")
