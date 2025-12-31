#!/usr/bin/env python
"""
Comprehensive database cleanup and enum type fix
"""
from app.core.database import engine
from sqlalchemy import text

print("\n" + "=" * 70)
print("COMPREHENSIVE DATABASE CLEANUP AND ENUM FIX")
print("=" * 70)

with engine.begin() as conn:
    # 1. Delete all records with invalid enum values
    print("\n1. Deleting records with invalid enum values...")
    print("-" * 70)
    
    result = conn.execute(text("""
        DELETE FROM pesantren_fasilitas 
        WHERE asrama = 'cukup_lengkap'
           OR ruang_belajar = 'cukup_lengkap'
           OR ruang_belajar = 'lengkap'
           OR fasilitas_transportasi = 'cukup_lengkap'
           OR akses_jalan = 'baik'
           OR akses_jalan = 'cukup_baik'
    """))
    print(f"   ✓ Deleted {result.rowcount} records with invalid enum values")
    
    # 2. Verify all enum type definitions are correct
    print("\n2. Verifying PostgreSQL enum types...")
    print("-" * 70)
    
    # Check kelayakan_enum
    result = conn.execute(text("""
        SELECT enumlabel FROM pg_enum 
        WHERE enumtypid = 'kelayakan_enum'::regtype
        ORDER BY enumlabel
    """))
    kelayakan_values = [row[0] for row in result]
    print(f"   kelayakan_enum values: {kelayakan_values}")
    expected_kelayakan = ['cukup', 'layak', 'tidak_layak']
    if sorted(kelayakan_values) == sorted(expected_kelayakan):
        print(f"   ✓ kelayakan_enum is CORRECT")
    else:
        print(f"   ⚠ WARNING: kelayakan_enum mismatch!")
        print(f"     Expected: {expected_kelayakan}")
        print(f"     Got: {kelayakan_values}")
    
    # Check kestabilan_enum if it exists
    result = conn.execute(text("""
        SELECT enumlabel FROM pg_enum 
        WHERE enumtypid = 'kestabilan_enum'::regtype
        ORDER BY enumlabel
    """))
    kestabilan_values = [row[0] for row in result]
    if kestabilan_values:
        print(f"   kestabilan_enum values: {kestabilan_values}")
        expected_kestabilan = ['tidak_ada', 'tidak_stabil', 'stabil']
        if sorted(kestabilan_values) == sorted(expected_kestabilan):
            print(f"   ✓ kestabilan_enum is CORRECT")
        else:
            print(f"   ⚠ WARNING: kestabilan_enum mismatch!")
            print(f"     Expected: {expected_kestabilan}")
            print(f"     Got: {kestabilan_values}")
    
    # Check fasilitas_transportasi_enum if it exists
    result = conn.execute(text("""
        SELECT enumlabel FROM pg_enum 
        WHERE enumtypid = 'fasilitas_transportasi_enum'::regtype
        ORDER BY enumlabel
    """))
    fasilitas_values = [row[0] for row in result]
    if fasilitas_values:
        print(f"   fasilitas_transportasi_enum values: {fasilitas_values}")
        expected_fasilitas = ['angkutan_umum', 'bus', 'kendaraan_pribadi', 'ojek']
        if sorted(fasilitas_values) == sorted(expected_fasilitas):
            print(f"   ✓ fasilitas_transportasi_enum is CORRECT")
        else:
            print(f"   ⚠ WARNING: fasilitas_transportasi_enum mismatch!")
            print(f"     Expected: {expected_fasilitas}")
            print(f"     Got: {fasilitas_values}")
    
    # Check akses_jalan_enum if it exists
    result = conn.execute(text("""
        SELECT enumlabel FROM pg_enum 
        WHERE enumtypid = 'akses_jalan_enum'::regtype
        ORDER BY enumlabel
    """))
    akses_values = [row[0] for row in result]
    if akses_values:
        print(f"   akses_jalan_enum values: {akses_values}")
        expected_akses = ['aspal', 'cor_block', 'kerikil', 'tanah']
        if sorted(akses_values) == sorted(expected_akses):
            print(f"   ✓ akses_jalan_enum is CORRECT")
        else:
            print(f"   ⚠ WARNING: akses_jalan_enum mismatch!")
            print(f"     Expected: {expected_akses}")
            print(f"     Got: {akses_values}")
    
    # 3. Verify data integrity
    print("\n3. Verifying data integrity...")
    print("-" * 70)
    
    result = conn.execute(text("SELECT COUNT(*) FROM pesantren_fasilitas"))
    count = result.scalar()
    print(f"   Total records in pesantren_fasilitas: {count}")
    
    # Check if any records still have invalid values
    result = conn.execute(text("""
        SELECT COUNT(*) FROM pesantren_fasilitas 
        WHERE (asrama IS NOT NULL AND asrama NOT IN ('layak', 'cukup', 'tidak_layak'))
           OR (ruang_belajar IS NOT NULL AND ruang_belajar NOT IN ('layak', 'cukup', 'tidak_layak'))
           OR (internet IS NOT NULL AND internet NOT IN ('stabil', 'tidak_stabil', 'tidak_ada'))
           OR (fasilitas_transportasi IS NOT NULL AND fasilitas_transportasi NOT IN ('bus', 'angkutan_umum', 'kendaraan_pribadi', 'ojek'))
           OR (akses_jalan IS NOT NULL AND akses_jalan NOT IN ('aspal', 'cor_block', 'tanah', 'kerikil'))
    """))
    invalid_count = result.scalar()
    if invalid_count == 0:
        print(f"   ✓ No invalid enum values found in any record")
    else:
        print(f"   ⚠ WARNING: Found {invalid_count} records with invalid enum values!")

print("\n" + "=" * 70)
print("DATABASE CLEANUP COMPLETED")
print("=" * 70 + "\n")
