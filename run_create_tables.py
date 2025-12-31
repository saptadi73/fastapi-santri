"""Execute SQL to create map tables."""
from app.core.database import engine
from sqlalchemy import text

with open('create_map_tables.sql', 'r') as f:
    sql = f.read()

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print('✅ Map tables created successfully!')

# Verify
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

if 'santri_map' in tables:
    print("✅ santri_map table exists")
    
if 'pesantren_map' in tables:
    print("✅ pesantren_map table exists")
