from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Get all tables
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    tables = [row[0] for row in result]
    print("Tables:", tables)
    
    # Drop all tables
    for table in tables:
        if table != 'spatial_ref_sys' and table != 'layer' and table != 'topology':
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                print(f"Dropped {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
    
    # Drop from alembic_version
    try:
        conn.execute(text('DELETE FROM alembic_version'))
        print("Cleared alembic_version")
    except:
        pass
    
    conn.commit()
    print("Done!")
