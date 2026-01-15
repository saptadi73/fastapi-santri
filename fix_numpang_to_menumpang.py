"""
Fix 'numpang' to 'menumpang' in status_rumah
"""
from app.core.database import engine
from sqlalchemy import text

def fix_numpang_to_menumpang():
    """Fix numpang -> menumpang"""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text("UPDATE santri_rumah SET status_rumah = 'menumpang' WHERE status_rumah = 'numpang'")
            )
            print(f"✓ Updated {result.rowcount} 'numpang' entries to 'menumpang'")
            
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
    fix_numpang_to_menumpang()
