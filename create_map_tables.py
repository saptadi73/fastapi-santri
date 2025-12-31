"""Create map tables."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Loading database...")
from app.core.database import engine
from sqlalchemy import text

# Drop orphan indexes if exist
print("Dropping orphan indexes...")
with engine.connect() as conn:
    try:
        conn.execute(text('DROP INDEX IF EXISTS idx_santri_map_lokasi'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_lokasi'))
        conn.execute(text('DROP INDEX IF EXISTS idx_santri_map_santri_id'))
        conn.execute(text('DROP INDEX IF EXISTS idx_santri_map_nama'))
        conn.execute(text('DROP INDEX IF EXISTS idx_santri_map_pesantren_id'))
        conn.execute(text('DROP INDEX IF EXISTS idx_santri_map_kategori'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_pesantren_id'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_nama'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_kabupaten'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_provinsi'))
        conn.execute(text('DROP INDEX IF EXISTS idx_pesantren_map_kategori'))
        conn.commit()
        print("✓ Dropped orphan indexes")
    except Exception as e:
        print(f"Note: {e}")

# Import all models
print("Loading models...")
from app.main import app  # Load all models

# Create tables
print("Creating map tables...")
from app.models.santri_map import SantriMap
from app.models.pesantren_map import PesantrenMap
from app.models.base import Base

Base.metadata.create_all(engine, tables=[
    SantriMap.__table__,
    PesantrenMap.__table__
])

print("✅ Map tables created successfully!")

# Verify
print("\nVerifying...")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'santri_map' in tables:
    print("✅ santri_map table exists")
    columns = [col['name'] for col in inspector.get_columns('santri_map')]
    print(f"   Columns: {', '.join(columns)}")
    
if 'pesantren_map' in tables:
    print("✅ pesantren_map table exists")
    columns = [col['name'] for col in inspector.get_columns('pesantren_map')]
    print(f"   Columns: {', '.join(columns)}")

print("\n✅ Done!")
