"""
Verify the jenis_kelamin values are now correct
"""
from app.core.database import engine
from sqlalchemy import text

def verify_jenis_kelamin():
    """Check that all jenis_kelamin values are now L or P"""
    with engine.connect() as connection:
        # Check for invalid values
        result = connection.execute(
            text("""SELECT DISTINCT jenis_kelamin FROM santri_pribadi""")
        )
        values = [row[0] for row in result]
        print("Current jenis_kelamin values in database:", values)
        
        # Check for invalid entries
        invalid = connection.execute(
            text("""SELECT COUNT(*) FROM santri_pribadi WHERE jenis_kelamin NOT IN ('L', 'P')""")
        )
        invalid_count = invalid.scalar()
        print(f"Invalid entries: {invalid_count}")
        
        if invalid_count == 0 and set(values) == {'L', 'P'}:
            print("✓ All jenis_kelamin values are correct!")
            return True
        else:
            print("✗ There are still invalid values!")
            return False

if __name__ == "__main__":
    verify_jenis_kelamin()
