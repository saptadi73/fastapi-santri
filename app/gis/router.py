from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/gis", tags=["GIS"])

# Admin boundary table/config. Ganti sesuai skema/tabel di database Anda.
ADMIN_SCHEMA = "public"  # kosongkan ("") jika tabel ada di search_path default
PROV_TABLE = "provinsi"
KAB_TABLE = "kabupaten"
KEC_TABLE = "kecamatan"


def _tbl(name: str) -> str:
    return f"{ADMIN_SCHEMA}.{name}" if ADMIN_SCHEMA else name


@router.get("/santri-points")
def santri_points(
    provinsi: str | None = None,
    kabupaten: str | None = None,
    kecamatan: str | None = None,
    db: Session = Depends(get_db),
):
    where = ["s.lokasi IS NOT NULL"]
    joins = []
    params: dict[str, str] = {}

    if provinsi:
        joins.append(f"JOIN {_tbl(PROV_TABLE)} p ON ST_Contains(p.geom, s.lokasi)")
        where.append("p.name_1 = :provinsi")
        params["provinsi"] = provinsi

    if kabupaten:
        joins.append(f"JOIN {_tbl(KAB_TABLE)} k ON ST_Contains(k.geom, s.lokasi)")
        where.append("k.name_2 = :kabupaten")
        params["kabupaten"] = kabupaten

    if kecamatan:
        joins.append(f"JOIN {_tbl(KEC_TABLE)} kc ON ST_Contains(kc.geom, s.lokasi)")
        where.append("kc.name_3 = :kecamatan")
        params["kecamatan"] = kecamatan

    sql = f"""
    SELECT jsonb_build_object(
      'type','FeatureCollection',
      'features', COALESCE(
        jsonb_agg(
          jsonb_build_object(
            'type','Feature',
            'geometry', ST_AsGeoJSON(s.lokasi)::jsonb,
            'properties', jsonb_build_object(
              'id', s.id,
              'nama', s.nama,
              'provinsi', s.provinsi,
              'kabupaten', s.kabupaten,
              'kecamatan', s.kecamatan
            )
          )
        ), '[]'::jsonb
      )
    )
    FROM santri_pribadi s
    {' '.join(joins)}
    WHERE {' AND '.join(where)};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"GIS query failed: {exc}")

@router.get("/heatmap")
def heatmap(db: Session = Depends(get_db)):
    sql = """
    SELECT
      ST_Y(lokasi) AS lat,
      ST_X(lokasi) AS lng,
      1 AS weight
    FROM santri_pribadi
    WHERE lokasi IS NOT NULL;
    """
    rows = db.execute(text(sql)).fetchall()

    return [
        {"lat": r.lat, "lng": r.lng, "weight": r.weight}
        for r in rows
    ]
