from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
import os
from app.auth.router import router as auth_router
from app.santri.router import router as santri_router
from app.gis.router import router as gis_router
from app.dashboard.router import router as dashboard_router
from app.routes.santri_pribadi_routes import router as santri_pribadi_router
from app.routes.santri_pribadi_alias_routes import router as santri_pribadi_alias_router

# Import models to ensure SQLAlchemy can find them
from app.santri.models import Santri  # noqa: F401
from app.models.pesantren_fisik import PesantrenFisik  # noqa: F401
from app.models.pesantren_fasilitas import PesantrenFasilitas  # noqa: F401
from app.models.pesantren_pendidikan import PesantrenPendidikan  # noqa: F401
from app.models.santri_pribadi import SantriPribadi  # noqa: F401
from app.models.pesantren_skor import PesantrenSkor  # noqa: F401
from app.models.foto_pesantren import FotoPesantren  # noqa: F401
from app.routes.santri_orangtua_routes import router as santri_orangtua_router
from app.routes.santri_rumah_routes import router as santri_rumah_router
from app.routes.santri_asset_routes import router as santri_asset_router
from app.routes.santri_bansos_routes import router as santri_bansos_router
from app.routes.santri_kesehatan_routes import router as santri_kesehatan_router
from app.routes.santri_pembiayaan_routes import router as santri_pembiayaan_router
from app.routes.score_routes import router as score_router
from app.routes.pondok_pesantren_routes import router as pondok_pesantren_router
from app.routes.pesantren_fisik_routes import router as pesantren_fisik_router
from app.routes.pesantren_fasilitas_routes import router as pesantren_fasilitas_router
from app.routes.pesantren_pendidikan_routes import router as pesantren_pendidikan_router
from app.routes.pesantren_score_routes import router as pesantren_score_router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title=settings.APP_NAME)

# CORS Configuration - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4000",
        "http://127.0.0.1:4000",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files for uploads
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth_router)
app.include_router(santri_router)
app.include_router(gis_router)
app.include_router(dashboard_router)
app.include_router(santri_pribadi_router)
app.include_router(santri_pribadi_alias_router)
app.include_router(santri_orangtua_router)
app.include_router(santri_rumah_router)
app.include_router(santri_asset_router)
app.include_router(santri_bansos_router)
app.include_router(santri_kesehatan_router)
app.include_router(santri_pembiayaan_router)
app.include_router(score_router)
app.include_router(pondok_pesantren_router)
app.include_router(pesantren_fisik_router)
app.include_router(pesantren_fasilitas_router)
app.include_router(pesantren_pendidikan_router)
app.include_router(pesantren_score_router)

@app.get("/")
def root():
    return {"status": "FastAPI Santri Backend Ready"}
