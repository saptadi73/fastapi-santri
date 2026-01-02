"""Test pesantren scoring with detailed breakdown."""
import importlib
import pkgutil
import json
from uuid import UUID
from app.core.database import SessionLocal
from app.services.pesantren_score_service import PesantrenScoreService
import app.models as models_pkg

# Register all models
[importlib.import_module(f'app.models.{m.name}') for m in pkgutil.iter_modules(models_pkg.__path__)]


def test_pesantren_breakdown():
    """Test pesantren scoring breakdown."""
    with SessionLocal() as db:
        from app.models.pondok_pesantren import PondokPesantren
        
        # Get first pesantren
        pesantren = db.query(PondokPesantren).first()
        
        if not pesantren:
            print("No pesantren found in database")
            return
        
        print(f"Testing Pesantren: {pesantren.nama}")
        print(f"ID: {pesantren.id}\n")
        
        # Calculate scoring
        svc = PesantrenScoreService(db)
        record, breakdown = svc.calculate_and_save(pesantren.id)
        
        print("=" * 60)
        print("HASIL SCORING PESANTREN")
        print("=" * 60)
        print(f"Skor Total       : {record.skor_total}")
        print(f"Kategori         : {record.kategori_kelayakan.upper()}")
        print(f"Metode           : {record.metode}")
        print(f"Versi            : {record.version}")
        
        print("\n" + "=" * 60)
        print("BREAKDOWN DIMENSI")
        print("=" * 60)
        
        for dim in breakdown['dimensi']:
            print(f"\n>> {dim['nama']}")
            print(f"   Skor        : {dim['skor']}/{dim['skor_maks']}")
            print(f"   Bobot       : {dim['bobot']:.1f}%")
            print(f"   Kontribusi  : {dim['kontribusi']:.2f}")
            print(f"   Interpretasi: {dim['interpretasi']}")
            
            if dim['detail']:
                print(f"   Detail Parameter:")
                for param in dim['detail']:
                    status = "[OK]" if param['skor'] >= 80 else "[!!]" if param['skor'] >= 60 else "[XX]"
                    print(f"      {status} {param['parameter']}: {param['nilai']} (skor: {param['skor']})")
        
        print("\n" + "=" * 60)
        print("INTERPRETASI KATEGORI")
        print("=" * 60)
        print(f"{breakdown['interpretasi_kategori']}")
        
        # Verify breakdown structure
        print("\n" + "=" * 60)
        print("VERIFIKASI STRUKTUR BREAKDOWN")
        print("=" * 60)
        
        checks = [
            ("dimensi" in breakdown, "[OK] Field 'dimensi' ada"),
            ("skor_total" in breakdown, "[OK] Field 'skor_total' ada"),
            ("kategori_kelayakan" in breakdown, "[OK] Field 'kategori_kelayakan' ada"),
            ("interpretasi_kategori" in breakdown, "[OK] Field 'interpretasi_kategori' ada"),
            (len(breakdown['dimensi']) == 4, "[OK] Jumlah dimensi = 4"),
        ]
        
        for check, message in checks:
            print(message if check else message.replace("[OK]", "[FAIL]"))
        
        # Test get_by_pesantren_id
        print("\n" + "=" * 60)
        print("TEST GET BY PESANTREN ID")
        print("=" * 60)
        
        result = svc.get_by_pesantren_id(pesantren.id)
        if result:
            rec2, breakdown2 = result
            print(f"[OK] Record ditemukan: skor_total = {rec2.skor_total}")
            print(f"[OK] Breakdown ada: {len(breakdown2['dimensi'])} dimensi")
            
            # Compare totals
            if rec2.skor_total == breakdown2['skor_total']:
                print(f"[OK] Konsistensi total: {rec2.skor_total} = {breakdown2['skor_total']}")
            else:
                print(f"[FAIL] Inkonsistensi total: {rec2.skor_total} != {breakdown2['skor_total']}")
        else:
            print("[FAIL] Record tidak ditemukan")
        
        print("\n" + "=" * 60)
        print("TEST SELESAI")
        print("=" * 60)
        
        # Export breakdown to JSON for inspection
        with open("pesantren_breakdown_sample.json", "w", encoding="utf-8") as f:
            json.dump(breakdown, f, indent=2, ensure_ascii=False)
        print("\nBreakdown detail disimpan ke: pesantren_breakdown_sample.json")


if __name__ == "__main__":
    test_pesantren_breakdown()
