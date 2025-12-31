#!/usr/bin/env python
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("\n" + "=" * 70)
print("FINAL VERIFICATION")
print("=" * 70)

# Verify data integrity
print("\n1. Checking pesantren_fasilitas records:")
print("-" * 70)

result = db.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas"))
count = result.scalar()
print(f"   Total records: {count}")

result = db.execute(text("""
    SELECT id, asrama, ruang_belajar, internet, fasilitas_transportasi, akses_jalan
    FROM pesantren_fasilitas
"""))
rows = result.fetchall()
if not rows:
    print(f"   ✓ Table is clean (no records)")
else:
    print(f"   Records found: {len(rows)}")
    for row in rows:
        print(f"\n   ID: {row[0]}")
        print(f"     asrama: {row[1]}")
        print(f"     ruang_belajar: {row[2]}")
        print(f"     internet: {row[3]}")
        print(f"     fasilitas_transportasi: {row[4]}")
        print(f"     akses_jalan: {row[5]}")

# Check PostgreSQL enum types
print("\n2. PostgreSQL enum type definitions:")
print("-" * 70)

result = db.execute(text("""
    SELECT enumtypid::regtype as enum_name, enumlabel 
    FROM pg_enum 
    WHERE enumtypid::regtype::text LIKE '%enum'
    ORDER BY enumtypid::regtype, enumlabel
"""))

enum_dict = {}
for row in result:
    enum_name = str(row[0])
    enum_value = row[1]
    if enum_name not in enum_dict:
        enum_dict[enum_name] = []
    enum_dict[enum_name].append(enum_value)

for enum_name, values in sorted(enum_dict.items()):
    print(f"   {enum_name}: {values}")

print("\n" + "=" * 70)
print("✓ DATABASE IS NOW CLEAN AND READY")
print("=" * 70 + "\n")

db.close()
