from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Fixing 'solar panel' to 'tenaga_surya'...")
    result = conn.execute(text("""
        UPDATE pesantren_fisik 
        SET sumber_listrik = 'tenaga_surya'
        WHERE sumber_listrik = 'solar panel'
    """))
    conn.commit()
    print(f"✅ Updated {result.rowcount} rows")
    
    print("\nVerifying sumber_listrik values:")
    result = conn.execute(text("""
        SELECT DISTINCT sumber_listrik, COUNT(*) as count
        FROM pesantren_fisik 
        WHERE sumber_listrik IS NOT NULL
        GROUP BY sumber_listrik
        ORDER BY sumber_listrik
    """))
    
    for row in result:
        print(f"  - {row[0]}: {row[1]} records")
