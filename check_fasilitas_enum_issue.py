"""Check pesantren_fasilitas enum values in database"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.database import settings

# Create engine
engine = create_engine(settings.database_url)

# Check the actual values in the database
with engine.connect() as conn:
    print("=== Checking pesantren_fasilitas enum fields ===\n")
    
    # Check what values exist for asrama
    result = conn.execute(text("""
        SELECT id, pesantren_id, asrama, ruang_belajar, internet
        FROM pesantren_fasilitas
        WHERE pesantren_id = 'ed1ecaf0-2034-4e83-886d-54430c2f7f9c'
        LIMIT 5
    """))
    
    print("Records for pesantren_id ed1ecaf0-2034-4e83-886d-54430c2f7f9c:")
    for row in result:
        print(f"  ID: {row.id}")
        print(f"  Pesantren ID: {row.pesantren_id}")
        print(f"  Asrama: {row.asrama} (type: {type(row.asrama)})")
        print(f"  Ruang Belajar: {row.ruang_belajar} (type: {type(row.ruang_belajar)})")
        print(f"  Internet: {row.internet} (type: {type(row.internet)})")
        print()
    
    # Check all unique values
    print("\n=== All unique enum values in table ===\n")
    result = conn.execute(text("""
        SELECT DISTINCT asrama FROM pesantren_fasilitas WHERE asrama IS NOT NULL
    """))
    print("Unique asrama values:")
    for row in result:
        print(f"  - {row.asrama} (type: {type(row.asrama)})")
    
    result = conn.execute(text("""
        SELECT DISTINCT ruang_belajar FROM pesantren_fasilitas WHERE ruang_belajar IS NOT NULL
    """))
    print("\nUnique ruang_belajar values:")
    for row in result:
        print(f"  - {row.ruang_belajar} (type: {type(row.ruang_belajar)})")
    
    result = conn.execute(text("""
        SELECT DISTINCT internet FROM pesantren_fasilitas WHERE internet IS NOT NULL
    """))
    print("\nUnique internet values:")
    for row in result:
        print(f"  - {row.internet} (type: {type(row.internet)})")

print("\n=== Done ===")
