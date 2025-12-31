"""Check santri_map data."""
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('SELECT santri_id, nama, skor_terakhir, kategori_kemiskinan FROM santri_map LIMIT 10')).fetchall()

print(f'\n✅ Records in santri_map: {len(result)}\n')
for r in result:
    print(f'  - {r[1]}: Score {r[2]} ({r[3]})')

db.close()
