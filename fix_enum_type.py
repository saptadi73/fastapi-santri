"""Drop and recreate the kelayakan_enum type with valid values only."""
from app.core.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    try:
        # Drop the old enum type
        conn.execute(text("DROP TYPE IF EXISTS kelayakan_enum CASCADE"))
        print("✓ Dropped old kelayakan_enum type")
        
        # Recreate with only valid values
        conn.execute(text("""
            CREATE TYPE kelayakan_enum AS ENUM (
                'layak',
                'cukup',
                'tidak_layak'
            )
        """))
        print("✓ Recreated kelayakan_enum with valid values: layak, cukup, tidak_layak")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

print("\n✓ Database enum type fixed successfully!")
