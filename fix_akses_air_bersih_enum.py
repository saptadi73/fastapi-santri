"""
Fix akses_air_bersih enum values
'terbatas' -> 'tidak_layak' (limited access = inadequate)
"""
from app.core.database import engine
from sqlalchemy import text

def fix_akses_air_bersih():
    """Fix akses_air_bersih enum values"""
    with engine.begin() as connection:
        try:
            # Get current distinct values
            result = connection.execute(
                text("SELECT DISTINCT akses_air_bersih FROM santri_rumah WHERE akses_air_bersih IS NOT NULL")
            )
            current_values = [row[0] for row in result]
            print(f"Current distinct akses_air_bersih values: {current_values}")
            
            # Count each value
            for val in current_values:
                result = connection.execute(
                    text("SELECT COUNT(*) FROM santri_rumah WHERE akses_air_bersih = :val"),
                    {"val": val}
                )
                count = result.scalar()
                print(f"  '{val}': {count} records")
            
            # Map 'terbatas' to 'tidak_layak'
            result = connection.execute(
                text("UPDATE santri_rumah SET akses_air_bersih = 'tidak_layak' WHERE akses_air_bersih = 'terbatas'")
            )
            print(f"\n✓ Updated {result.rowcount} 'terbatas' entries to 'tidak_layak'")
            
            # Verify final values
            result = connection.execute(
                text("SELECT DISTINCT akses_air_bersih FROM santri_rumah WHERE akses_air_bersih IS NOT NULL")
            )
            final_values = [row[0] for row in result]
            print(f"\nFinal distinct akses_air_bersih values: {final_values}")
            
            # Check for invalid values
            invalid = connection.execute(
                text("SELECT COUNT(*) FROM santri_rumah WHERE akses_air_bersih NOT IN ('layak', 'tidak_layak') AND akses_air_bersih IS NOT NULL")
            )
            invalid_count = invalid.scalar()
            print(f"Invalid entries remaining: {invalid_count}")
            
            if invalid_count == 0:
                print("✓ All akses_air_bersih values are now valid!")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_akses_air_bersih()
