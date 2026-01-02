"""Check pesantren_skor table columns"""
from sqlalchemy import inspect, create_engine, text
from app.core.config import settings

engine = create_engine(settings.database_url)

# Use raw SQL to check columns
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'pesantren_skor'
        ORDER BY ordinal_position
    """))
    
    print("Columns in pesantren_skor table:")
    for row in result:
        print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
