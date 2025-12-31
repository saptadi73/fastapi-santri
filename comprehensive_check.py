#!/usr/bin/env python
from app.core.database import SessionLocal, engine
from sqlalchemy import text

print("=" * 60)
print("COMPREHENSIVE DATABASE CHECK")
print("=" * 60)

# 1. Check PostgreSQL Enum Type Definition
print("\n1. PostgreSQL ENUM Type Definitions:")
print("-" * 60)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT enumtypid::regtype as enum_name, enumlabel 
        FROM pg_enum 
        WHERE enumtypid::regtype::text LIKE '%_enum'
        ORDER BY enumtypid::regtype, enumlabel
    """))
    for row in result:
        print(f"  {row[0]}: {row[1]}")

# 2. Check all data in pesantren_fasilitas
print("\n2. Data in pesantren_fasilitas Table:")
print("-" * 60)
db = SessionLocal()
result = db.execute(text("""
    SELECT id, asrama, ruang_belajar, internet, fasilitas_transportasi, akses_jalan
    FROM pesantren_fasilitas
"""))
rows = result.fetchall()
if not rows:
    print("  No records found")
else:
    for row in rows:
        print(f"\n  ID: {row[0]}")
        print(f"    asrama: {row[1]}")
        print(f"    ruang_belajar: {row[2]}")
        print(f"    internet: {row[3]}")
        print(f"    fasilitas_transportasi: {row[4]}")
        print(f"    akses_jalan: {row[5]}")

# 3. Check for any NULL or invalid values
print("\n3. Check for problematic values:")
print("-" * 60)
result = db.execute(text("""
    SELECT COUNT(*) as total_records
    FROM pesantren_fasilitas
"""))
print(f"  Total records: {result.scalar()}")

result = db.execute(text("""
    SELECT COUNT(*) as records_with_cukup_lengkap
    FROM pesantren_fasilitas 
    WHERE asrama = 'cukup_lengkap' 
       OR ruang_belajar = 'cukup_lengkap'
       OR fasilitas_transportasi = 'cukup_lengkap'
"""))
print(f"  Records with 'cukup_lengkap': {result.scalar()}")

# 4. Check Alembic migrations
print("\n4. Migration history in database:")
print("-" * 60)
result = db.execute(text("""
    SELECT version, description, installed_on 
    FROM alembic_version 
    ORDER BY installed_on DESC 
    LIMIT 5
"""))
rows = result.fetchall()
if rows:
    for row in rows:
        print(f"  {row[0]}: {row[1]} ({row[2]})")
else:
    print("  No migration table found or empty")

db.close()
print("\n" + "=" * 60)
