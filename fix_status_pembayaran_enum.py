"""
Fix status_pembayaran enum values
'tepat_waktu' -> 'lancar' (on-time payment = smooth/current)
"""
from app.core.database import engine
from sqlalchemy import text

def fix_status_pembayaran():
    """Fix status_pembayaran enum values"""
    with engine.begin() as connection:
        try:
            # Get current distinct values
            result = connection.execute(
                text("SELECT DISTINCT status_pembayaran FROM santri_pembiayaan WHERE status_pembayaran IS NOT NULL")
            )
            current_values = [row[0] for row in result]
            print(f"Current distinct status_pembayaran values: {current_values}")
            
            # Count each value
            for val in current_values:
                result = connection.execute(
                    text("SELECT COUNT(*) FROM santri_pembiayaan WHERE status_pembayaran = :val"),
                    {"val": val}
                )
                count = result.scalar()
                print(f"  '{val}': {count} records")
            
            # Map 'tepat_waktu' to 'lancar'
            result = connection.execute(
                text("UPDATE santri_pembiayaan SET status_pembayaran = 'lancar' WHERE status_pembayaran = 'tepat_waktu'")
            )
            print(f"\n✓ Updated {result.rowcount} 'tepat_waktu' entries to 'lancar'")
            
            # Verify final values
            result = connection.execute(
                text("SELECT DISTINCT status_pembayaran FROM santri_pembiayaan WHERE status_pembayaran IS NOT NULL")
            )
            final_values = [row[0] for row in result]
            print(f"\nFinal distinct status_pembayaran values: {final_values}")
            
            # Check for invalid values
            invalid = connection.execute(
                text("SELECT COUNT(*) FROM santri_pembiayaan WHERE status_pembayaran NOT IN ('lancar', 'terlambat', 'menunggak') AND status_pembayaran IS NOT NULL")
            )
            invalid_count = invalid.scalar()
            print(f"Invalid entries remaining: {invalid_count}")
            
            if invalid_count == 0:
                print("✓ All status_pembayaran values are now valid!")
            
        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    fix_status_pembayaran()
