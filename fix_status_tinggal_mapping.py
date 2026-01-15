"""
Fix status_tinggal mapping to correct enum values
'Pulang Pergi' or 'pulang pergi' -> 'pp'
'Mondok' -> 'mondok'
Keep 'mukim' as is
"""
from app.core.database import engine
from sqlalchemy import text

def fix_status_tinggal_mapping():
    """Map all status_tinggal values to valid enum values"""
    with engine.begin() as connection:
        try:
            # Map 'pulang pergi' to 'pp'
            result = connection.execute(
                text("UPDATE santri_pribadi SET status_tinggal = 'pp' WHERE LOWER(status_tinggal) = 'pulang pergi'")
            )
            print(f"✓ Updated {result.rowcount} 'pulang pergi' entries to 'pp'")
            
            # Make sure all mondok values are lowercase
            result = connection.execute(
                text("UPDATE santri_pribadi SET status_tinggal = 'mondok' WHERE LOWER(status_tinggal) = 'mondok' AND status_tinggal != 'mondok'")
            )
            print(f"✓ Normalized {result.rowcount} 'mondok' entries to lowercase")
            
            # Verify all values are now valid
            result = connection.execute(
                text("SELECT DISTINCT status_tinggal FROM santri_pribadi WHERE status_tinggal IS NOT NULL")
            )
            final_values = [row[0] for row in result]
            print(f"Final distinct status_tinggal values: {final_values}")
            
            # Check for invalid values
            invalid = connection.execute(
                text("SELECT COUNT(*) FROM santri_pribadi WHERE status_tinggal NOT IN ('mondok', 'pp', 'mukim') AND status_tinggal IS NOT NULL")
            )
            invalid_count = invalid.scalar()
            print(f"Invalid entries remaining: {invalid_count}")
            
            if invalid_count == 0:
                print("✓ All status_tinggal values are now valid!")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_status_tinggal_mapping()
