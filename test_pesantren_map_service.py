from app.core.database import SessionLocal
from app.services.pesantren_map_service import PesantrenMapService
from uuid import UUID
from sqlalchemy import text

# Import all models to ensure relationships work
from app.santri.models import Santri  # noqa: F401
from app.models.pondok_pesantren import PondokPesantren  # noqa: F401
from app.models.pesantren_fisik import PesantrenFisik  # noqa: F401
from app.models.pesantren_fasilitas import PesantrenFasilitas  # noqa: F401
from app.models.pesantren_pendidikan import PesantrenPendidikan  # noqa: F401
from app.models.pesantren_skor import PesantrenSkor  # noqa: F401
from app.models.pesantren_map import PesantrenMap  # noqa: F401
from app.models.santri_pribadi import SantriPribadi  # noqa: F401
from app.models.santri_orangtua import SantriOrangtua  # noqa: F401
from app.models.santri_rumah import SantriRumah  # noqa: F401
from app.models.santri_asset import SantriAsset  # noqa: F401
from app.models.santri_bansos import SantriBansos  # noqa: F401
from app.models.santri_kesehatan import SantriKesehatan  # noqa: F401
from app.models.santri_pembiayaan import SantriPembiayaan  # noqa: F401
from app.models.santri_skor import SantriSkor  # noqa: F401
from app.models.santri_map import SantriMap  # noqa: F401
from app.models.foto_orangtua import FotoOrangtua  # noqa: F401
from app.models.foto_rumah import FotoRumah  # noqa: F401
from app.models.foto_santri import FotoSantri  # noqa: F401
from app.models.foto_asset import FotoAsset  # noqa: F401
from app.models.foto_pesantren import FotoPesantren  # noqa: F401

db = SessionLocal()

pesantren_id = UUID("bfc0e58b-de57-4f22-84e3-5c36cd2002de")
skor_total = 94
kategori = "sangat_layak"

print("Testing PesantrenMapService.upsert_from_scoring()...")
print(f"  Pesantren ID: {pesantren_id}")
print(f"  Score: {skor_total}")
print(f"  Category: {kategori}")

try:
    map_service = PesantrenMapService(db)
    result = map_service.upsert_from_scoring(pesantren_id, skor_total, kategori)
    print(f"\n✅ SUCCESS! Map record created/updated:")
    print(f"  - ID: {result.id}")
    print(f"  - Nama: {result.nama}")
    print(f"  - Skor: {result.skor_terakhir}")
    print(f"  - Kategori: {result.kategori_kelayakan}")
    
    # Verify in database
    count_result = db.execute(text("SELECT COUNT(*) FROM pesantren_map")).fetchone()
    print(f"\n📊 Total records in pesantren_map: {count_result[0]}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

db.close()
