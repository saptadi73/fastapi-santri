"""
Fix jenis_kelamin values in santri_pribadi table
Convert 'Laki-laki' -> 'L' and 'Perempuan' -> 'P'
"""
from app.core.database import engine
from sqlalchemy import text

def fix_jenis_kelamin_values():
    """Convert full gender names to enum codes"""
    with engine.begin() as connection:
        try:
            # Update Laki-laki to L
            result1 = connection.execute(
                text("UPDATE santri_pribadi SET jenis_kelamin = 'L' WHERE jenis_kelamin = 'Laki-laki'")
            )
            print(f"✓ Updated {result1.rowcount} 'Laki-laki' entries to 'L'")
            
            # Update Perempuan to P
            result2 = connection.execute(
                text("UPDATE santri_pribadi SET jenis_kelamin = 'P' WHERE jenis_kelamin = 'Perempuan'")
            )
            print(f"✓ Updated {result2.rowcount} 'Perempuan' entries to 'P'")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_jenis_kelamin_values()
