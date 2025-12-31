"""Repository for aggregating santri-related data from multiple tables."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.santri_pribadi import SantriPribadi
from app.models.santri_orangtua import SantriOrangtua
from app.models.santri_rumah import SantriRumah
from app.models.santri_asset import SantriAsset
from app.models.santri_pembiayaan import SantriPembiayaan
from app.models.santri_kesehatan import SantriKesehatan
from app.models.santri_bansos import SantriBansos


class SantriDataRepository:
    """Aggregates a santri's data across domain tables."""

    def __init__(self, db: Session):
        self.db = db

    def get_pribadi(self, santri_id: UUID) -> Optional[SantriPribadi]:
        return self.db.query(SantriPribadi).filter(SantriPribadi.id == santri_id).first()

    def get_rumah(self, santri_id: UUID) -> Optional[SantriRumah]:
        return self.db.query(SantriRumah).filter(SantriRumah.santri_id == santri_id).first()

    def get_assets(self, santri_id: UUID) -> List[SantriAsset]:
        return self.db.query(SantriAsset).filter(SantriAsset.santri_id == santri_id).all()

    def get_pembiayaan(self, santri_id: UUID) -> Optional[SantriPembiayaan]:
        return self.db.query(SantriPembiayaan).filter(SantriPembiayaan.santri_id == santri_id).first()

    def get_kesehatan(self, santri_id: UUID) -> Optional[SantriKesehatan]:
        return self.db.query(SantriKesehatan).filter(SantriKesehatan.santri_id == santri_id).first()

    def get_bansos(self, santri_id: UUID) -> Optional[SantriBansos]:
        return self.db.query(SantriBansos).filter(SantriBansos.santri_id == santri_id).first()

    def get_all(self, santri_id: UUID) -> Dict[str, Any]:
        return {
            "pribadi": self.get_pribadi(santri_id),
            "rumah": self.get_rumah(santri_id),
            "assets": self.get_assets(santri_id),
            "pembiayaan": self.get_pembiayaan(santri_id),
            "kesehatan": self.get_kesehatan(santri_id),
            "bansos": self.get_bansos(santri_id),
        }

    # Config-driven parameter fetchers
    def get_param_value(self, santri_id: UUID, sumber: str, kode: str) -> Any:
        """Return a value for a parameter `kode` from `sumber` based on available models.

        This maps the config needs to existing schema fields, deriving when necessary.
        """
        if sumber == "santri_orangtua":
            ot = self.db.query(SantriOrangtua).filter(SantriOrangtua.santri_id == santri_id).first()
            if not ot:
                return None
            if kode == "penghasilan_bulanan" or kode == "pendapatan_bulanan":
                return getattr(ot, "pendapatan_bulanan", None)
            if kode == "pekerjaan":
                return getattr(ot, "pekerjaan", None)
            if kode == "pendidikan":
                return getattr(ot, "pendidikan", None)
            if kode == "jumlah_tanggungan":
                # Not available; default to 0 (can be refined later)
                return 0
            if kode == "status_pekerjaan":
                # Derive category from pekerjaan free-text
                pekerjaan = (getattr(ot, "pekerjaan", "") or "").lower()
                if any(k in pekerjaan for k in ["buruh", "kuli", "serabutan"]):
                    return "buruh"
                if any(k in pekerjaan for k in ["kontrak", "bagian", "honor"]):
                    return "tidak_tetap"
                if pekerjaan:
                    return "tetap"
                return None

        if sumber == "santri_rumah":
            r = self.db.query(SantriRumah).filter(SantriRumah.santri_id == santri_id).first()
            if not r:
                return None
            if kode == "status_kepemilikan" or kode == "status_rumah":
                return getattr(r, "status_rumah", None)
            if kode == "jenis_lantai":
                return getattr(r, "jenis_lantai", None)
            if kode == "jenis_dinding":
                return getattr(r, "jenis_dinding", None)
            if kode == "jenis_atap":
                return getattr(r, "jenis_atap", None)
            if kode == "akses_air_bersih":
                return getattr(r, "akses_air_bersih", None)
            if kode == "daya_listrik_va":
                return getattr(r, "daya_listrik_va", None)
            if kode == "luas_per_orang":
                # No explicit fields; default to None (no score)
                return None
            if kode == "lantai":
                return getattr(r, "jenis_lantai", None)
            if kode == "sanitasi":
                # Derive: akses_air_bersih "layak" -> True; else False
                return (getattr(r, "akses_air_bersih", None) == "layak")

        if sumber == "santri_aset":
            assets = self.get_assets(santri_id)
            if kode == "motor":
                return sum(a.jumlah or 0 for a in assets if getattr(a, "jenis_aset", None) == "motor")
            if kode == "mobil":
                return sum(a.jumlah or 0 for a in assets if getattr(a, "jenis_aset", None) == "mobil")
            if kode == "lahan":
                # We do not store area; derive presence as 0 or 0.5
                has_lahan = any(
                    str(getattr(a, "jenis_aset", "") or "").lower() == "lahan"
                    for a in assets
                )
                return 0.0 if not has_lahan else 0.5

        if sumber == "santri_pembiayaan":
            p = self.db.query(SantriPembiayaan).filter(SantriPembiayaan.santri_id == santri_id).first()
            if not p:
                return None
            if kode == "sumber_biaya":
                return getattr(p, "sumber_biaya", None)
            if kode == "tunggakan":
                return (getattr(p, "tunggakan_bulan", 0) or 0) > 0

        if sumber == "santri_kesehatan":
            k = self.db.query(SantriKesehatan).filter(SantriKesehatan.santri_id == santri_id).first()
            if not k:
                return None
            if kode == "penyakit_kronis":
                # Derive from riwayat_penyakit presence
                rp = getattr(k, "riwayat_penyakit", "") or ""
                return bool(rp.strip())
            if kode == "bpjs_aktif":
                # Unknown; default False (vulnerable)
                return False

        if sumber == "santri_bansos":
            b = self.db.query(SantriBansos).filter(SantriBansos.santri_id == santri_id).first()
            if not b:
                return None
            if kode == "pernah_menerima":
                flags = [b.pkh, b.bpnt, b.pip, b.kis_pbi, b.blt_desa]
                return any(bool(f) for f in flags)
            if kode == "dtks":
                # Not tracked; default False
                return False

        return None
