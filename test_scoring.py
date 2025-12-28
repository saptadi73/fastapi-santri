#!/usr/bin/env python3
"""Quick test of scoring system."""

from app.core.database import SessionLocal
from app.services.score_service import ScoreService

# Import all models to register them
from app.models.santri_pribadi import SantriPribadi
from app.models.santri_orangtua import SantriOrangtua
from app.models.santri_rumah import SantriRumah
from app.models.santri_asset import SantriAsset
from app.models.santri_pembiayaan import SantriPembiayaan
from app.models.santri_kesehatan import SantriKesehatan
from app.models.santri_bansos import SantriBansos
from app.models.santri_skor import SantriSkor
from app.models.foto_santri import FotoSantri
from app.models.foto_orangtua import FotoOrangtua
from app.models.foto_asset import FotoAsset

db = SessionLocal()
try:
    santri = db.query(SantriPribadi).first()
    if santri:
        print(f"Testing santri: {santri.nama} (ID: {santri.id})")
        svc = ScoreService(db)
        record = svc.calculate_and_save(santri.id)
        print(f"\nScoring Result:")
        print(f"  Total: {record.skor_total}")
        print(f"  Kategori: {record.kategori_kemiskinan}")
        print(f"  Metode: {record.metode}")
        print(f"  Version: {record.version}")
        print(f"\nPer-Component:")
        print(f"  Ekonomi: {record.skor_ekonomi}")
        print(f"  Rumah: {record.skor_rumah}")
        print(f"  Aset: {record.skor_aset}")
        print(f"  Pembiayaan: {record.skor_pembiayaan}")
        print(f"  Kesehatan: {record.skor_kesehatan}")
        print(f"  Bansos: {record.skor_bansos}")
    else:
        print("No santri found in database")
finally:
    db.close()
