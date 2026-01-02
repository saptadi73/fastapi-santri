#!/usr/bin/env python3
"""Add missing columns to database directly via SQL."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fastapi_santri")
engine = create_engine(DB_URL)

# List of ALTER statements to add missing columns
alter_statements = [
    # pesantren_fasilitas
    """ALTER TABLE pesantren_fasilitas 
       ADD COLUMN IF NOT EXISTS jumlah_kamar_mandi INTEGER;""",
    
    """ALTER TABLE pesantren_fasilitas 
       ADD COLUMN IF NOT EXISTS sumber_air VARCHAR;""",
    
    # pesantren_skor - Rename skor_kelayakan_fisik to skor_fisik
    """ALTER TABLE pesantren_skor 
       RENAME COLUMN skor_kelayakan_fisik TO skor_fisik;""",
    
    """ALTER TABLE pesantren_skor 
       ADD COLUMN IF NOT EXISTS skor_fasilitas INTEGER;""",
    
    """ALTER TABLE pesantren_skor 
       ADD COLUMN IF NOT EXISTS skor_pendidikan INTEGER;""",
    
    # pondok_pesantren
    """ALTER TABLE pondok_pesantren 
       ADD COLUMN IF NOT EXISTS kontak_telepon VARCHAR(15);""",
    
    # santri
    """ALTER TABLE santri 
       ADD COLUMN IF NOT EXISTS status VARCHAR;""",
    
    # santri_pembiayaan
    """ALTER TABLE santri_pembiayaan 
       ADD COLUMN IF NOT EXISTS sumber_pembiayaan VARCHAR;""",
    
    # santri_pribadi
    """ALTER TABLE santri_pribadi 
       ADD COLUMN IF NOT EXISTS latitude FLOAT;""",
    
    """ALTER TABLE santri_pribadi 
       ADD COLUMN IF NOT EXISTS longitude FLOAT;""",
    
    # santri_skor
    """ALTER TABLE santri_skor 
       ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;""",
    
    """ALTER TABLE santri_skor 
       ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;""",
]

try:
    with engine.connect() as conn:
        for stmt in alter_statements:
            try:
                conn.execute(text(stmt))
                print(f"✅ {stmt.split()[0:5]}")
            except Exception as e:
                # Might fail if column already exists, skip
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print(f"⏭️  {stmt.split()[0:5]} (already exists)")
                else:
                    print(f"❌ {stmt.split()[0:5]} - {str(e)[:50]}")
        
        conn.commit()
    
    print("\n✅ All columns added successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
