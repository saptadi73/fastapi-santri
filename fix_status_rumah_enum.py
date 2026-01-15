"""
Fix status_rumah values in santri_rumah table
'sewa' should map to 'kontrak'
"""
from app.core.database import engine
from sqlalchemy import text

def fix_status_rumah_values():
    """Fix status_rumah enum values"""
    with engine.begin() as connection:
        try:
            # Get current distinct values
            result = connection.execute(
                text("SELECT DISTINCT status_rumah FROM santri_rumah WHERE status_rumah IS NOT NULL")
            )
            current_values = [row[0] for row in result]
            print(f"Current distinct status_rumah values: {current_values}")
            
            # Map 'sewa' to 'kontrak'
            result = connection.execute(
                text("UPDATE santri_rumah SET status_rumah = 'kontrak' WHERE LOWER(status_rumah) = 'sewa'")
            )
            print(f"✓ Updated {result.rowcount} 'sewa' entries to 'kontrak'")
            
            # Normalize any capitalized values
            for old_value in ['milik_sendiri', 'kontrak', 'menumpang']:
                result = connection.execute(
                    text(f"UPDATE santri_rumah SET status_rumah = :new_val WHERE LOWER(status_rumah) = :old_val AND status_rumah != :new_val"),
                    {"new_val": old_value, "old_val": old_value}
                )
                if result.rowcount > 0:
                    print(f"✓ Normalized {result.rowcount} '{old_value}' entries to lowercase")
            
            # Verify all values are now valid
            result = connection.execute(
                text("SELECT DISTINCT status_rumah FROM santri_rumah WHERE status_rumah IS NOT NULL")
            )
            final_values = [row[0] for row in result]
            print(f"Final distinct status_rumah values: {final_values}")
            
            # Check for invalid values
            invalid = connection.execute(
                text("SELECT COUNT(*) FROM santri_rumah WHERE status_rumah NOT IN ('milik_sendiri', 'kontrak', 'menumpang') AND status_rumah IS NOT NULL")
            )
            invalid_count = invalid.scalar()
            print(f"Invalid entries remaining: {invalid_count}")
            
            if invalid_count == 0:
                print("✓ All status_rumah values are now valid!")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_status_rumah_values()
