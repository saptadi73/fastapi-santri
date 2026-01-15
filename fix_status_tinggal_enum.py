"""
Fix status_tinggal values in santri_pribadi table
Convert capitalized values to lowercase: 'Mondok' -> 'mondok', 'Pp' -> 'pp', 'Mukim' -> 'mukim'
"""
from app.core.database import engine
from sqlalchemy import text

def fix_status_tinggal_values():
    """Convert status_tinggal values to lowercase"""
    with engine.begin() as connection:
        try:
            # Get current distinct values
            result = connection.execute(
                text("SELECT DISTINCT status_tinggal FROM santri_pribadi WHERE status_tinggal IS NOT NULL")
            )
            current_values = [row[0] for row in result]
            print(f"Current distinct status_tinggal values: {current_values}")
            
            # Update all values to lowercase
            for old_value in current_values:
                if old_value:  # Skip NULL values
                    new_value = old_value.lower()
                    if old_value != new_value:
                        result = connection.execute(
                            text(f"UPDATE santri_pribadi SET status_tinggal = :new_val WHERE status_tinggal = :old_val"),
                            {"new_val": new_value, "old_val": old_value}
                        )
                        print(f"✓ Updated {result.rowcount} '{old_value}' entries to '{new_value}'")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_status_tinggal_values()
