"""Test script to verify pembiayaan scoring for a specific santri."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID

from app.core.config import settings
from app.repositories.santri_data_repository import SantriDataRepository
from app.rules.scoring_rules import calculate_scores_from_config

# Setup database
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Test santri
santri_id = UUID('1eee8ac2-2d33-4795-8691-ca5f165d2972')
repo = SantriDataRepository(db)

print("=" * 60)
print("Testing get_param_value for pembiayaan:")
print("=" * 60)
print(f"sumber_biaya: {repo.get_param_value(santri_id, 'santri_pembiayaan', 'sumber_biaya')}")
print(f"status_pembayaran: {repo.get_param_value(santri_id, 'santri_pembiayaan', 'status_pembayaran')}")
print(f"tunggakan_bulan: {repo.get_param_value(santri_id, 'santri_pembiayaan', 'tunggakan_bulan')}")

print("\n" + "=" * 60)
print("Calculating scores:")
print("=" * 60)
scores, total, kategori, metode, version, breakdown = calculate_scores_from_config(repo, santri_id)

print(f"\nPembiayaan Score: {scores.get('skor_pembiayaan', 0)}")
print(f"Total Score: {total}")
print(f"Kategori: {kategori}")

print("\n" + "=" * 60)
print("Pembiayaan Dimension Details:")
print("=" * 60)
pembiayaan_dims = [d for d in breakdown['dimensi'] if d['nama'] == 'Pembiayaan Pendidikan']
if pembiayaan_dims:
    pembiayaan_dim = pembiayaan_dims[0]
    print(f"Skor: {pembiayaan_dim['skor']} / {pembiayaan_dim['skor_maks']}")
    print(f"Interpretasi: {pembiayaan_dim['interpretasi']}")
    print("\nParameter Details:")
    for param in pembiayaan_dim.get('detail', []):
        print(f"  {param['parameter']}: {param['nilai']} -> skor {param['skor']}")

db.close()
print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
