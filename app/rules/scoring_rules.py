"""Scoring rules for Santri data.

Notes:
- Higher score indicates higher vulnerability/poverty.
- Thresholds and weights are placeholders; adjust per policy.
"""
from typing import Dict, Any, List, Tuple, Optional, cast
from app.rules.config_loader import load_scoring_config
from app.repositories.santri_data_repository import SantriDataRepository
from uuid import UUID


def _val_str(obj: Any, field: str) -> Optional[str]:
    v = getattr(obj, field, None)
    return None if v is None else cast(str, v)


def _val_int(obj: Any, field: str) -> Optional[int]:
    v = getattr(obj, field, None)
    return None if v is None else cast(int, v)


def _val_bool(obj: Any, field: str) -> bool:
    v = getattr(obj, field, None)
    return bool(v) if v is not None else False


def score_rumah(rumah: Any | None) -> int:
    if not rumah:
        return 0
    score = 0
    status_rumah = _val_str(rumah, "status_rumah")
    jenis_lantai = _val_str(rumah, "jenis_lantai")
    jenis_dinding = _val_str(rumah, "jenis_dinding")
    jenis_atap = _val_str(rumah, "jenis_atap")
    akses_air = _val_str(rumah, "akses_air_bersih")
    daya_listrik = _val_str(rumah, "daya_listrik_va")

    score += {"milik_sendiri": 0, "kontrak": 5, "menumpang": 8}.get(status_rumah or "", 0)
    score += {"tanah": 7, "semen": 3, "keramik": 0}.get(jenis_lantai or "", 0)
    score += {"bambu": 6, "kayu": 3, "tembok": 0}.get(jenis_dinding or "", 0)
    score += {"rumbia": 6, "seng": 3, "genteng": 1, "beton": 0}.get(jenis_atap or "", 0)
    score += {"tidak_layak": 7, "layak": 0}.get(akses_air or "", 0)
    if daya_listrik is not None and daya_listrik != "":
        score += {"450": 5, "900": 3, "1300": 1, "2200": 0, "3500": 0, "5500": 0}.get(daya_listrik, 0)
    return score


def score_aset(assets: List[Any]) -> int:
    if not assets:
        return 10  # no assets -> higher vulnerability
    score = 0
    for a in assets:
        jenis_aset = _val_str(a, "jenis_aset") or ""
        jumlah = _val_int(a, "jumlah") or 0
        nilai = _val_int(a, "nilai_perkiraan") or 0

        base = {"motor": 2, "mobil": 0, "sepeda": 3, "hp": 2, "laptop": 0, "lahan": 0, "ternak": 1, "alat_kerja": 1, "lainnya": 1}.get(jenis_aset, 1)
        score += max(0, base - min(jumlah, 3))  # more items reduce vulnerability for some types
        if nilai > 50000000:
            score -= 2  # high-value asset reduces vulnerability
    return max(0, score)


def score_pembiayaan(p: Any | None) -> int:
    if not p:
        return 5  # unknown -> mild vulnerability
    score = 0
    status = _val_str(p, "status_pembayaran") or ""
    tunggakan = _val_int(p, "tunggakan_bulan") or 0
    biaya = _val_int(p, "biaya_per_bulan") or 0

    score += {"lancar": 0, "terlambat": 4, "menunggak": 8}.get(status, 2)
    if tunggakan >= 3:
        score += 4
    if biaya > 500000:
        score += 2
    return score


def score_kesehatan(k: Any | None) -> int:
    if not k:
        return 0
    status = _val_str(k, "status_gizi") or ""
    return {"baik": 0, "kurang": 6, "lebih": 2}.get(status, 0)


def score_bansos(b: Any | None) -> int:
    if not b:
        return 0
    flags = [
        _val_bool(b, "pkh"),
        _val_bool(b, "bpnt"),
        _val_bool(b, "pip"),
        _val_bool(b, "kis_pbi"),
        _val_bool(b, "blt_desa"),
    ]
    base = sum(3 for f in flags if f)
    # Extra boost if multiple programs
    if base >= 9:
        base += 2
    return base


def score_ekonomi(assets: List[Any], pembiayaan: Any | None) -> int:
    # Proxy using assets and payment burden
    aset_component = max(0, 8 - len(assets))  # fewer assets -> more vulnerability
    pembiayaan_component = 0
    if pembiayaan:
        status = _val_str(pembiayaan, "status_pembayaran") or ""
        pembiayaan_component += {"lancar": 0, "terlambat": 3, "menunggak": 6}.get(status, 2)
        tunggakan = _val_int(pembiayaan, "tunggakan_bulan") or 0
        if tunggakan >= 2:
            pembiayaan_component += 3
    return aset_component + pembiayaan_component


def aggregate_scores(data: Dict[str, Any]) -> Tuple[Dict[str, int], int, str]:
    rumah = score_rumah(data.get("rumah"))
    aset = score_aset(data.get("assets") or [])
    pembiayaan = score_pembiayaan(data.get("pembiayaan"))
    kesehatan = score_kesehatan(data.get("kesehatan"))
    bansos = score_bansos(data.get("bansos"))
    ekonomi = score_ekonomi(data.get("assets") or [], data.get("pembiayaan"))

    per_component = {
        "skor_ekonomi": ekonomi,
        "skor_rumah": rumah,
        "skor_aset": aset,
        "skor_pembiayaan": pembiayaan,
        "skor_kesehatan": kesehatan,
        "skor_bansos": bansos,
    }
    total = sum(per_component.values())
    # Category thresholds (placeholder)
    if total >= 30:
        kategori = "miskin"
    elif total >= 20:
        kategori = "rentan"
    else:
        kategori = "cukup"
    return per_component, total, kategori


def _apply_rule(op: str, value: Any, target: Any) -> bool:
    # Support basic operators: ==, <, <=, >=, in
    try:
        if op == "==":
            return target == value
        if op == "<":
            return (target is not None) and (float(target) < float(value))
        if op == "<=":
            return (target is not None) and (float(target) <= float(value))
        if op == ">=":
            return (target is not None) and (float(target) >= float(value))
        if op == "in":
            return target in value  # value expected to be list
    except Exception:
        return False
    return False


def calculate_scores_from_config(repo: SantriDataRepository, santri_id: UUID) -> Tuple[Dict[str, int], int, str, str, str, Dict[str, Any]]:
    """Compute scores using scoring.json config via repository param values.

    Returns per-component scores, total (0-100), kategori label, metode, version, and breakdown details.
    """
    cfg = load_scoring_config()
    meta = cfg.get("metadata", {})
    metode = meta.get("metode", "config")
    version = meta.get("version", "1.0.0")
    total_max = meta.get("skor_maks_total", 100)

    dimensi = cfg.get("dimensi", {})
    per_component: Dict[str, int] = {}
    total_score_float = 0.0
    breakdown_dimensi = []

    # Interpretasi mapping untuk kategori
    kategori_interpretasi = {
        "Sangat Miskin": "Kondisi sangat buruk, memerlukan bantuan segera",
        "Miskin": "Kondisi buruk, memerlukan bantuan",
        "Rentan": "Kondisi sedang, rentan jatuh miskin",
        "Tidak Miskin": "Kondisi baik, tidak memerlukan bantuan"
    }

    for dim_key, dim_conf in dimensi.items():
        bobot = float(dim_conf.get("bobot", 0))
        skor_maks = int(dim_conf.get("skor_maks", 0))
        params = dim_conf.get("parameters", [])

        raw_dim = 0
        detail_params = []
        
        for p in params:
            kode = p.get("kode")
            sumber = p.get("sumber")
            rules = p.get("rules", [])
            label = p.get("label", kode)
            
            if not kode or not sumber:
                continue
                
            val = repo.get_param_value(santri_id, sumber, kode)
            skor_param = 0
            
            for r in rules:
                op = r.get("operator")
                rv = r.get("value")
                skor = int(r.get("skor", 0))
                if op and _apply_rule(op, rv, val):
                    skor_param = skor
                    raw_dim += skor
                    detail_params.append({
                        "parameter": label,
                        "nilai": str(val) if val is not None else "Tidak ada data",
                        "skor": skor_param
                    })
                    break  # first matching rule applies
            
            # Jika tidak ada rule yang match, tetap catat nilainya
            if skor_param == 0 and val is not None:
                detail_params.append({
                    "parameter": label,
                    "nilai": str(val),
                    "skor": 0
                })

        raw_dim = min(raw_dim, skor_maks)
        # Dimension weighted contribution
        contrib = bobot * raw_dim
        total_score_float += contrib
        per_component[f"skor_{dim_key}"] = int(round(raw_dim))
        
        # Interpretasi dimensi berdasarkan skor
        if raw_dim == 0:
            interpretasi = "Sangat Baik"
        elif raw_dim <= skor_maks * 0.25:
            interpretasi = "Baik"
        elif raw_dim <= skor_maks * 0.5:
            interpretasi = "Sedang"
        elif raw_dim <= skor_maks * 0.75:
            interpretasi = "Buruk"
        else:
            interpretasi = "Sangat Buruk"
        
        # Nama dimensi yang lebih friendly
        nama_dimensi_map = {
            "ekonomi": "Ekonomi",
            "rumah": "Kondisi Rumah",
            "aset": "Kepemilikan Aset",
            "pembiayaan": "Pembiayaan Pendidikan",
            "kesehatan": "Kesehatan",
            "bansos": "Penerima Bantuan Sosial"
        }
        
        breakdown_dimensi.append({
            "nama": nama_dimensi_map.get(dim_key, dim_key.title()),
            "skor": int(round(raw_dim)),
            "skor_maks": skor_maks,
            "bobot": bobot * 100,  # Convert to percentage
            "kontribusi": round(contrib, 2),
            "interpretasi": interpretasi,
            "detail": detail_params if detail_params else None
        })

    # Normalise to total_max if needed: current design assumes skor_maks weighted sum already in 0-100 scale
    total_int = int(round(total_score_float))

    # Category mapping
    kategori = ""
    kategori_list = sorted(cfg.get("kategori_kemiskinan", []), key=lambda x: int(x.get("min", 0)), reverse=True)
    for item in kategori_list:
        if total_int >= int(item.get("min", 0)):
            kategori = item.get("label", "Tidak Miskin")
            break
    if not kategori:
        kategori = "Tidak Miskin"
    
    breakdown = {
        "dimensi": breakdown_dimensi,
        "skor_total": total_int,
        "kategori_kemiskinan": kategori,
        "interpretasi_kategori": kategori_interpretasi.get(kategori, "")
    }

    return per_component, total_int, kategori, metode, version, breakdown
