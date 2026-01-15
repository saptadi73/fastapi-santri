"""
Fix enum values in database - replace spaces with underscores and fix case sensitivity
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def fix_enum_values():
    """Fix all enum values that have spaces instead of underscores or wrong case"""
    
    with engine.connect() as conn:
        # Fix kondisi_bangunan
        print("=" * 60)
        print("Checking kondisi_bangunan values...")
        result = conn.execute(text("""
            SELECT DISTINCT kondisi_bangunan 
            FROM pesantren_fisik 
            ORDER BY kondisi_bangunan
        """))
        
        print("Current values:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\nFixing 'semi permanen' to 'semi_permanen'...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET kondisi_bangunan = 'semi_permanen'
            WHERE kondisi_bangunan = 'semi permanen'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        print("\nFixing 'non permanen' to 'non_permanen' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET kondisi_bangunan = 'non_permanen'
            WHERE kondisi_bangunan = 'non permanen'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        # Fix sumber_air
        print("\n" + "=" * 60)
        print("Checking sumber_air values...")
        result = conn.execute(text("""
            SELECT DISTINCT sumber_air 
            FROM pesantren_fisik 
            WHERE sumber_air IS NOT NULL
            ORDER BY sumber_air
        """))
        
        print("Current values:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\nFixing 'pdam' to 'PDAM' (uppercase)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sumber_air = 'PDAM'
            WHERE LOWER(sumber_air) = 'pdam'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        print("\nFixing 'berbagai macam' to 'berbagai_macam' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sumber_air = 'berbagai_macam'
            WHERE sumber_air = 'berbagai macam'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        # Fix sumber_listrik
        print("\n" + "=" * 60)
        print("Checking sumber_listrik values...")
        result = conn.execute(text("""
            SELECT DISTINCT sumber_listrik 
            FROM pesantren_fisik 
            WHERE sumber_listrik IS NOT NULL
            ORDER BY sumber_listrik
        """))
        
        print("Current values:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\nFixing 'pln' to 'PLN' (uppercase)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sumber_listrik = 'PLN'
            WHERE LOWER(sumber_listrik) = 'pln'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        print("\nFixing 'listrik tidak ada' to 'listrik_tidak_ada' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sumber_listrik = 'listrik_tidak_ada'
            WHERE sumber_listrik = 'listrik tidak ada'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        print("\nFixing 'tenaga surya' to 'tenaga_surya' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sumber_listrik = 'tenaga_surya'
            WHERE sumber_listrik = 'tenaga surya'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        # Fix sanitasi
        print("\n" + "=" * 60)
        print("Checking sanitasi values...")
        result = conn.execute(text("""
            SELECT DISTINCT sanitasi 
            FROM pesantren_fisik 
            ORDER BY sanitasi
        """))
        
        print("Current values:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\nFixing 'tidak layak' to 'tidak_layak' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET sanitasi = 'tidak_layak'
            WHERE sanitasi = 'tidak layak'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        # Fix air_bersih
        print("\n" + "=" * 60)
        print("Checking air_bersih values...")
        result = conn.execute(text("""
            SELECT DISTINCT air_bersih 
            FROM pesantren_fisik 
            ORDER BY air_bersih
        """))
        
        print("Current values:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\nFixing 'tidak tersedia' to 'tidak_tersedia' (if exists)...")
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET air_bersih = 'tidak_tersedia'
            WHERE air_bersih = 'tidak tersedia'
        """))
        conn.commit()
        print(f"Updated {result.rowcount} rows")
        
        # Fix other potential enum issues
        print("\n" + "=" * 60)
        print("Checking for other enum fields with spaces...")
        
        # Fix fasilitas_mck
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET fasilitas_mck = 'kurang_lengkap'
            WHERE fasilitas_mck = 'kurang lengkap'
        """))
        conn.commit()
        if result.rowcount > 0:
            print(f"Fixed fasilitas_mck: {result.rowcount} rows")
        
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET fasilitas_mck = 'tidak_layak'
            WHERE fasilitas_mck = 'tidak layak'
        """))
        conn.commit()
        if result.rowcount > 0:
            print(f"Fixed fasilitas_mck tidak_layak: {result.rowcount} rows")
        
        # Fix jenis_atap
        result = conn.execute(text("""
            UPDATE pesantren_fisik 
            SET jenis_atap = 'genteng_tanah_liat'
            WHERE jenis_atap = 'genteng tanah liat'
        """))
        conn.commit()
        if result.rowcount > 0:
            print(f"Fixed jenis_atap: {result.rowcount} rows")
        
        print("\n" + "=" * 60)
        print("✅ All enum values fixed!")
        print("=" * 60)
        
        # Verification
        print("\nVerifying final values...")
        result = conn.execute(text("""
            SELECT DISTINCT kondisi_bangunan, COUNT(*) as count
            FROM pesantren_fisik 
            GROUP BY kondisi_bangunan
            ORDER BY kondisi_bangunan
        """))
        
        print("\nFinal kondisi_bangunan values:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} records")
        
        result = conn.execute(text("""
            SELECT DISTINCT sumber_air, COUNT(*) as count
            FROM pesantren_fisik 
            WHERE sumber_air IS NOT NULL
            GROUP BY sumber_air
            ORDER BY sumber_air
        """))
        
        print("\nFinal sumber_air values:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} records")

if __name__ == "__main__":
    print("Starting enum value fix...")
    print("=" * 60)
    try:
        fix_enum_values()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
