from fastapi import FastAPI
from app.core.config import settings
from app.auth.router import router as auth_router
from app.santri.router import router as santri_router
from app.gis.router import router as gis_router
from app.dashboard.router import router as dashboard_router
from app.routes.santri_pribadi_routes import router as santri_pribadi_router
from app.routes.santri_orangtua_routes import router as santri_orangtua_router
from app.routes.santri_rumah_routes import router as santri_rumah_router
from app.routes.santri_asset_routes import router as santri_asset_router
from app.routes.santri_bansos_routes import router as santri_bansos_router
from app.routes.santri_kesehatan_routes import router as santri_kesehatan_router
from app.routes.santri_pembiayaan_routes import router as santri_pembiayaan_router
from app.routes.score_routes import router as score_router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title=settings.APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # Port Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(santri_router)
app.include_router(gis_router)
app.include_router(dashboard_router)
app.include_router(santri_pribadi_router)
app.include_router(santri_orangtua_router)
app.include_router(santri_rumah_router)
app.include_router(santri_asset_router)
app.include_router(santri_bansos_router)
app.include_router(santri_kesehatan_router)
app.include_router(santri_pembiayaan_router)
app.include_router(score_router)

@app.get("/")
def root():
    return {"status": "FastAPI Santri Backend Ready"}
