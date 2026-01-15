from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Checking fasilitas_mck values...")
    result = conn.execute(text("""
        SELECT DISTINCT fasilitas_mck, COUNT(*) as count
        FROM pesantren_fisik 
        WHERE fasilitas_mck IS NOT NULL
        GROUP BY fasilitas_mck
        ORDER BY fasilitas_mck
    """))
    
    print("Current fasilitas_mck values:")
    for row in result:
        print(f"  - '{row[0]}': {row[1]} records")
    
    print("\nFixing 'tidak ada' to 'tidak_layak'...")
    result = conn.execute(text("""
        UPDATE pesantren_fisik 
        SET fasilitas_mck = 'tidak_layak'
        WHERE fasilitas_mck = 'tidak ada'
    """))
    conn.commit()
    print(f"✅ Updated {result.rowcount} rows")
    
    print("\nFixing 'kurang lengkap' to 'kurang_lengkap' (if exists)...")
    result = conn.execute(text("""
        UPDATE pesantren_fisik 
        SET fasilitas_mck = 'kurang_lengkap'
        WHERE fasilitas_mck = 'kurang lengkap'
    """))
    conn.commit()
    print(f"✅ Updated {result.rowcount} rows")
    
    print("\nVerifying final fasilitas_mck values:")
    result = conn.execute(text("""
        SELECT DISTINCT fasilitas_mck, COUNT(*) as count
        FROM pesantren_fisik 
        WHERE fasilitas_mck IS NOT NULL
        GROUP BY fasilitas_mck
        ORDER BY fasilitas_mck
    """))
    
    for row in result:
        print(f"  - '{row[0]}': {row[1]} records")
