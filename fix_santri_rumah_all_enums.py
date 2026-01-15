"""
Fix invalid enum values in santri_rumah table:
- 'marmer' -> 'keramik' (similar floor material)
- 'batako' -> 'tembok' (wall building material)
- 'asbes' -> 'seng' (roofing material)
- 'genteng_beton' -> 'beton' (concrete roofing)
"""
from app.core.database import engine
from sqlalchemy import text

def fix_santri_rumah_enums():
    """Fix invalid enum values in santri_rumah"""
    with engine.begin() as connection:
        try:
            # Fix jenis_lantai: marmer -> keramik
            result = connection.execute(
                text("UPDATE santri_rumah SET jenis_lantai = 'keramik' WHERE jenis_lantai = 'marmer'")
            )
            print(f"✓ Updated {result.rowcount} 'marmer' entries to 'keramik'")
            
            # Fix jenis_dinding: batako -> tembok
            result = connection.execute(
                text("UPDATE santri_rumah SET jenis_dinding = 'tembok' WHERE jenis_dinding = 'batako'")
            )
            print(f"✓ Updated {result.rowcount} 'batako' entries to 'tembok'")
            
            # Fix jenis_atap: asbes -> seng
            result = connection.execute(
                text("UPDATE santri_rumah SET jenis_atap = 'seng' WHERE jenis_atap = 'asbes'")
            )
            print(f"✓ Updated {result.rowcount} 'asbes' entries to 'seng'")
            
            # Fix jenis_atap: genteng_beton -> beton
            result = connection.execute(
                text("UPDATE santri_rumah SET jenis_atap = 'beton' WHERE jenis_atap = 'genteng_beton'")
            )
            print(f"✓ Updated {result.rowcount} 'genteng_beton' entries to 'beton'")
            
            # Verify
            print("\nFinal verification:")
            fields = {
                'jenis_lantai': ['tanah', 'semen', 'keramik'],
                'jenis_dinding': ['bambu', 'kayu', 'tembok'],
                'jenis_atap': ['rumbia', 'seng', 'genteng', 'beton'],
            }
            
            for field, valid_values in fields.items():
                result = connection.execute(
                    text(f"SELECT DISTINCT {field} FROM santri_rumah WHERE {field} IS NOT NULL")
                )
                current = [r[0] for r in result]
                invalid = [v for v in current if v not in valid_values]
                if invalid:
                    print(f"✗ {field}: Still has invalid values {invalid}")
                else:
                    print(f"✓ {field}: All valid {current}")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_santri_rumah_enums()
