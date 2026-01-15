from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Define all enum columns and their expected values
ENUM_FIXES = {
    'keamanan_bangunan': {
        'tidak aman': 'tidak_aman',
    },
    'status_bangunan': {
        'milik sendiri': 'milik_sendiri',
    },
    'jenis_atap': {
        'genteng tanah liat': 'genteng_tanah_liat',
        'tenaga surya': 'tenaga_surya',
    },
    'sumber_listrik': {
        'listrik tidak ada': 'listrik_tidak_ada',
        'tenaga surya': 'tenaga_surya',
    },
    'kualitas_air_bersih': {
        'layak minum': 'layak_minum',
    }
}

with engine.connect() as conn:
    print("=" * 70)
    print("COMPREHENSIVE ENUM VALUE FIX")
    print("=" * 70)
    
    for column, fixes in ENUM_FIXES.items():
        print(f"\nChecking {column}...")
        
        # Check current values
        try:
            result = conn.execute(text(f"""
                SELECT DISTINCT {column}, COUNT(*) as count
                FROM pesantren_fisik 
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                ORDER BY {column}
            """))
            
            values = list(result)
            if values:
                print(f"Current values:")
                for row in values:
                    print(f"  - '{row[0]}': {row[1]} records")
                
                # Apply fixes
                for wrong_val, correct_val in fixes.items():
                    result = conn.execute(text(f"""
                        UPDATE pesantren_fisik 
                        SET {column} = :correct
                        WHERE {column} = :wrong
                    """), {"correct": correct_val, "wrong": wrong_val})
                    
                    if result.rowcount > 0:
                        conn.commit()
                        print(f"  ✅ Fixed '{wrong_val}' → '{correct_val}': {result.rowcount} rows")
            else:
                print(f"  No data in {column}")
        except Exception as e:
            print(f"  ⚠️ Error checking {column}: {e}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION - All enum columns")
    print("=" * 70)
    
    # List all enum columns to check
    enum_columns = [
        'kondisi_bangunan', 'status_bangunan', 'sanitasi', 'air_bersih',
        'keamanan_bangunan', 'sumber_air', 'fasilitas_mck', 'jenis_lantai',
        'jenis_atap', 'jenis_dinding', 'sumber_listrik', 'kualitas_air_bersih',
        'kestabilan_listrik'
    ]
    
    for column in enum_columns:
        try:
            result = conn.execute(text(f"""
                SELECT DISTINCT {column}, COUNT(*) as count
                FROM pesantren_fisik 
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                ORDER BY {column}
                LIMIT 10
            """))
            
            values = list(result)
            if values:
                print(f"\n{column}:")
                for row in values:
                    # Check if value has spaces (potential issue)
                    val = row[0]
                    marker = "⚠️" if " " in str(val) and "_" not in str(val) else "✓"
                    print(f"  {marker} '{val}': {row[1]} records")
        except Exception as e:
            print(f"\n{column}: Column not found or error - {e}")
    
    print("\n" + "=" * 70)
    print("✅ Comprehensive enum fix complete!")
    print("=" * 70)
