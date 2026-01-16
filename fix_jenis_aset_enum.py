"""
Fix jenis_aset enum values
Map 'sapi' and 'kambing' to 'ternak'
"""
from app.core.database import engine
from sqlalchemy import text

def fix_jenis_aset():
    """Fix jenis_aset enum values"""
    with engine.begin() as connection:
        try:
            # Get current distinct values
            result = connection.execute(
                text("SELECT DISTINCT jenis_aset FROM santri_asset WHERE jenis_aset IS NOT NULL")
            )
            current_values = [row[0] for row in result]
            print(f"Current distinct jenis_aset values: {current_values}")
            
            # Count each problematic value
            for val in ['sapi', 'kambing']:
                result = connection.execute(
                    text("SELECT COUNT(*) FROM santri_asset WHERE jenis_aset = :val"),
                    {"val": val}
                )
                count = result.scalar()
                if count > 0:
                    print(f"  '{val}': {count} records")
            
            # Map 'sapi' to 'ternak'
            result = connection.execute(
                text("UPDATE santri_asset SET jenis_aset = 'ternak' WHERE jenis_aset = 'sapi'")
            )
            print(f"\n✓ Updated {result.rowcount} 'sapi' entries to 'ternak'")
            
            # Map 'kambing' to 'ternak'
            result = connection.execute(
                text("UPDATE santri_asset SET jenis_aset = 'ternak' WHERE jenis_aset = 'kambing'")
            )
            print(f"✓ Updated {result.rowcount} 'kambing' entries to 'ternak'")
            
            # Verify final values
            result = connection.execute(
                text("SELECT DISTINCT jenis_aset FROM santri_asset WHERE jenis_aset IS NOT NULL")
            )
            final_values = [row[0] for row in result]
            print(f"\nFinal distinct jenis_aset values: {final_values}")
            
            # Check for invalid values
            valid_values = ['motor', 'mobil', 'sepeda', 'hp', 'laptop', 'lahan', 'ternak', 'alat_kerja', 'lainnya']
            invalid = connection.execute(
                text(f"SELECT COUNT(*) FROM santri_asset WHERE jenis_aset NOT IN ({','.join([':val'+str(i) for i in range(len(valid_values))])}) AND jenis_aset IS NOT NULL"),
                {f'val{i}': val for i, val in enumerate(valid_values)}
            )
            invalid_count = invalid.scalar()
            print(f"Invalid entries remaining: {invalid_count}")
            
            if invalid_count == 0:
                print("✓ All jenis_aset values are now valid!")
            else:
                # Show what invalid values remain
                result = connection.execute(
                    text(f"SELECT DISTINCT jenis_aset FROM santri_asset WHERE jenis_aset NOT IN ({','.join([':val'+str(i) for i in range(len(valid_values))])}) AND jenis_aset IS NOT NULL"),
                    {f'val{i}': val for i, val in enumerate(valid_values)}
                )
                remaining = [row[0] for row in result]
                print(f"  Remaining invalid values: {remaining}")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_jenis_aset()
