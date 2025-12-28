import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load DATABASE_URL from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set in .env")

sql_path = Path(__file__).parent / "ddl.sql"
sql_text = sql_path.read_text(encoding="utf-8")

print(f"Connecting: {DATABASE_URL}")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

print(f"Applying DDL from {sql_path}...")
cur.execute(sql_text)
print("DDL applied.")

print("Verifying tables exist...")
cur.execute("""
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'santri_pribadi','santri_bansos','santri_pembiayaan','santri_orangtua','santri_kesehatan',
    'santri_rumah','santri_asset'
  )
ORDER BY table_name;
""")
rows = cur.fetchall()
for r in rows:
    print("-", r[0])

cur.close()
conn.close()
print("Done.")
