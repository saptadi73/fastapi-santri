"""
Check database schema - lihat kolom apa yang ada di santri_pribadi dan santri_skor
"""
from app.core.database import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()

# Check santri_pribadi table
print("=" * 80)
print("CHECKING: santri_pribadi TABLE")
print("=" * 80)

try:
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    print(f"Available tables: {tables}\n")
    
    if "santri_pribadi" in tables:
        columns = inspector.get_columns("santri_pribadi")
        print(f"Columns in santri_pribadi:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("❌ santri_pribadi table not found!")
    
    print("\n" + "=" * 80)
    print("CHECKING: santri_skor TABLE")
    print("=" * 80)
    
    if "santri_skor" in tables:
        columns = inspector.get_columns("santri_skor")
        print(f"Columns in santri_skor:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("❌ santri_skor table not found!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

db.close()
