from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check default values
result = db.execute(text("""
    SELECT column_name, column_default, data_type
    FROM information_schema.columns 
    WHERE table_name = 'pesantren_fasilitas' 
    AND column_default IS NOT NULL 
    ORDER BY column_name
"""))

print("=== Columns with DEFAULT values ===")
for row in result:
    print(f"{row[0]}: {row[1]} (type: {row[2]})")

# Check table constraints
result2 = db.execute(text("""
    SELECT constraint_name, constraint_type
    FROM information_schema.table_constraints
    WHERE table_name = 'pesantren_fasilitas'
"""))

print("\n=== Table Constraints ===")
for row in result2:
    print(f"{row[0]}: {row[1]}")
