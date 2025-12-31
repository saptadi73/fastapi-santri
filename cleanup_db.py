"""Delete the problematic record with invalid enum values."""
from app.core.database import engine, SessionLocal
from sqlalchemy import text

with engine.begin() as conn:
    # Delete the problematic record
    conn.execute(text("DELETE FROM pesantren_fasilitas WHERE id = '1b65e80c-5bae-461f-b28e-7b1d8a6e0705'"))
    print("✓ Deleted invalid pesantren_fasilitas record")

# Verify
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM pesantren_fasilitas'))
count = result.scalar()
print(f"✓ Remaining records: {count}")
db.close()
