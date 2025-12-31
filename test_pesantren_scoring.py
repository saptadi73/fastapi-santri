#!/usr/bin/env python3
"""Quick test of pesantren scoring system."""

from app.core.database import SessionLocal
from app.services.pesantren_scoring_service import PesantrenScoringService
from app.models.pondok_pesantren import PondokPesantren

db = SessionLocal()
try:
    pesantren = db.query(PondokPesantren).first()
    if pesantren:
        print(f"Testing pesantren: {pesantren.nama} (ID: {pesantren.id})")
        svc = PesantrenScoringService(db)
        record = svc.calculate_and_save(pesantren.id)
        print(f"\nScoring Result:")
        print(f"  Total: {record.skor_total}")
        print(f"  Kategori: {record.kategori_kelayakan}")
        print(f"  Metode: {record.metode}")
        print(f"  Version: {record.version}")
        print(f"\nPer-Dimension:")
        print(f"  Kelayakan Fisik: {record.skor_kelayakan_fisik}")
        print(f"  Air & Sanitasi: {record.skor_air_sanitasi}")
        print(f"  Fasilitas Pendukung: {record.skor_fasilitas_pendukung}")
        print(f"  Mutu Pendidikan: {record.skor_mutu_pendidikan}")
    else:
        print("No pesantren found in database")
finally:
    db.close()
