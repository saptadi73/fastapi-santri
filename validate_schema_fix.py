"""Validate that the pesantren_skor schema is fixed"""
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings
from app.models.pesantren_skor import PesantrenSkor

# Get database columns
engine = create_engine(settings.database_url)
db_inspector = inspect(engine)
db_columns = {col['name'] for col in db_inspector.get_columns('pesantren_skor')}

# Get model columns  
model_mapper = inspect(PesantrenSkor)
model_columns = {col.name for col in model_mapper.columns}

print("=" * 60)
print("DATABASE vs MODEL VALIDATION")
print("=" * 60)

print(f"\nDatabase columns: {sorted(db_columns)}")
print(f"\nModel columns: {sorted(model_columns)}")

missing_in_model = db_columns - model_columns
missing_in_db = model_columns - db_columns

if missing_in_model:
    print(f"\n❌ Missing in model: {missing_in_model}")
else:
    print("\n✅ All database columns are in the model")

if missing_in_db:
    print(f"❌ Missing in database: {missing_in_db}")
else:
    print("✅ All model columns are in the database")

if not missing_in_model and not missing_in_db:
    print("\n✅ SCHEMA IS FULLY ALIGNED!")
    
    # Test a query
    print("\nTesting query execution...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT pesantren_id, skor_fisik, skor_total 
                FROM pesantren_skor 
                LIMIT 1
            """))
            row = result.fetchone()
            if row:
                print(f"✅ Query successful! Sample data: pesantren_id={row[0]}, skor_fisik={row[1]}, skor_total={row[2]}")
            else:
                print("✅ Query successful! (No data in table yet)")
    except Exception as e:
        print(f"❌ Query failed: {e}")
else:
    print("\n❌ SCHEMA IS NOT ALIGNED - FIX REQUIRED")
