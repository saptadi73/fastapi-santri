"""Fix invalid numeric enum values in pesantren_fasilitas table"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.database import settings

# Create engine
engine = create_engine(settings.database_url)

print("=== Fixing pesantren_fasilitas enum values ===\n")

# Mapping numeric values to proper enum values
# These appear to be quality/quantity indicators that need to be mapped to kelayakan
def map_numeric_to_kelayakan(numeric_value):
    """Map numeric values to kelayakan enum values"""
    if numeric_value is None:
        return None
    
    try:
        num = int(numeric_value)
        # Map based on reasonable ranges
        if num >= 5:  # Good quantity/quality
            return 'layak'
        elif num >= 2:  # Moderate quantity/quality
            return 'cukup'
        else:  # Low quantity/quality
            return 'tidak_layak'
    except (ValueError, TypeError):
        # If it's already a valid enum value, return it
        if numeric_value in ['layak', 'cukup', 'tidak_layak']:
            return numeric_value
        # Default to 'cukup' for unknown values
        return 'cukup'

with engine.begin() as conn:
    # First, check all records with numeric values
    result = conn.execute(text("""
        SELECT id, pesantren_id, asrama, ruang_belajar
        FROM pesantren_fasilitas
        WHERE asrama ~ '^[0-9]+$' OR ruang_belajar ~ '^[0-9]+$'
    """))
    
    records_to_fix = list(result)
    print(f"Found {len(records_to_fix)} records with numeric enum values\n")
    
    fixed_count = 0
    for row in records_to_fix:
        record_id = row.id
        asrama_value = row.asrama
        ruang_belajar_value = row.ruang_belajar
        
        # Map values
        new_asrama = map_numeric_to_kelayakan(asrama_value)
        new_ruang_belajar = map_numeric_to_kelayakan(ruang_belajar_value)
        
        print(f"Record {record_id}:")
        print(f"  Asrama: {asrama_value} -> {new_asrama}")
        print(f"  Ruang Belajar: {ruang_belajar_value} -> {new_ruang_belajar}")
        
        # Update the record
        conn.execute(text("""
            UPDATE pesantren_fasilitas
            SET asrama = :new_asrama,
                ruang_belajar = :new_ruang_belajar
            WHERE id = :record_id
        """), {
            'new_asrama': new_asrama,
            'new_ruang_belajar': new_ruang_belajar,
            'record_id': record_id
        })
        
        fixed_count += 1
    
    print(f"\n=== Fixed {fixed_count} records ===")
    
    # Verify the fix
    print("\n=== Verifying fix ===\n")
    result = conn.execute(text("""
        SELECT DISTINCT asrama FROM pesantren_fasilitas WHERE asrama IS NOT NULL
    """))
    print("Unique asrama values after fix:")
    for row in result:
        print(f"  - {row.asrama}")
    
    result = conn.execute(text("""
        SELECT DISTINCT ruang_belajar FROM pesantren_fasilitas WHERE ruang_belajar IS NOT NULL  
    """))
    print("\nUnique ruang_belajar values after fix:")
    for row in result:
        print(f"  - {row.ruang_belajar}")
    
    print("\n=== Done ===")
