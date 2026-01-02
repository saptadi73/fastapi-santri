#!/usr/bin/env python3
"""Verify all missing columns have been added."""

import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)
inspector = inspect(engine)

# Expected columns from schema_context.json
expected = {
    'pesantren_fasilitas': ['jumlah_kamar_mandi', 'sumber_air'],
    'pesantren_skor': ['skor_fisik', 'skor_fasilitas', 'skor_pendidikan'],
    'pondok_pesantren': ['kontak_telepon'],
    'santri': ['status'],
    'santri_pembiayaan': ['sumber_pembiayaan'],
    'santri_pribadi': ['latitude', 'longitude'],
    'santri_skor': ['created_at', 'updated_at']
}

issues = []
success_count = 0

for table, cols in expected.items():
    actual_cols = [c['name'] for c in inspector.get_columns(table)]
    for col in cols:
        if col in actual_cols:
            success_count += 1
            print(f"OK: {table}.{col}")
        else:
            issues.append(f"{table}.{col}")
            print(f"MISSING: {table}.{col}")

print(f"\n=== SUMMARY ===")
print(f"Success: {success_count}/{success_count + len(issues)}")
if issues:
    print(f"Still missing: {issues}")
else:
    print("All columns verified!")
