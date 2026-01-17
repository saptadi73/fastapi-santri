"""Find admin boundary tables"""
from app.core.database import get_db
from sqlalchemy import text

db = next(get_db())
result = db.execute(text("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname='public' 
    AND (
        tablename LIKE '%adm%' 
        OR tablename LIKE '%bound%' 
        OR tablename LIKE '%kab%' 
        OR tablename LIKE '%prov%'
        OR tablename LIKE '%idn%'
    )
    ORDER BY tablename
"""))
tables = [r[0] for r in result]
print("Admin boundary tables found:")
for t in tables:
    print(f"  - {t}")

if not tables:
    print("No admin boundary tables found!")
    print("\nAll tables in public schema:")
    result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
    for r in result:
        print(f"  - {r[0]}")
