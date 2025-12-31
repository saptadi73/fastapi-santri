#!/usr/bin/env python
from app.core.database import engine
from sqlalchemy import text, event

print("\nForce deleting problematic record...")

# Try direct delete without ORM
with engine.begin() as conn:
    # First, check constraints
    result = conn.execute(text("""
        SELECT constraint_name, constraint_type 
        FROM information_schema.table_constraints 
        WHERE table_name = 'pesantren_fasilitas'
    """))
    print("Constraints on pesantren_fasilitas:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
    
    # Delete using raw SQL - bypass any ORM constraints
    result = conn.execute(text("""
        DELETE FROM pesantren_fasilitas 
        WHERE id = 'bd77bca0-bb2d-4ab0-ab97-35f3d1149b43'
    """))
    print(f"\n✓ Deleted {result.rowcount} records")

# Verify deletion
from app.core.database import SessionLocal
db = SessionLocal()
result = db.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas"))
count = result.scalar()
print(f"✓ Remaining records: {count}")
db.close()
