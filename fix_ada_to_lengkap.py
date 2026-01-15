from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Mapping 'ada' to 'lengkap' for fasilitas_mck...")
    result = conn.execute(text("""
        UPDATE pesantren_fisik 
        SET fasilitas_mck = 'lengkap'
        WHERE fasilitas_mck = 'ada'
    """))
    conn.commit()
    print(f"✅ Updated {result.rowcount} rows")
    
    print("\nFinal fasilitas_mck values:")
    result = conn.execute(text("""
        SELECT DISTINCT fasilitas_mck, COUNT(*) as count
        FROM pesantren_fisik 
        WHERE fasilitas_mck IS NOT NULL
        GROUP BY fasilitas_mck
        ORDER BY fasilitas_mck
    """))
    
    for row in result:
        print(f"  - {row[0]}: {row[1]} records")
