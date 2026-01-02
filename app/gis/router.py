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
    kategori: str | None = None,
    pesantren_id: str | None = None,
    db: Session = Depends(get_db),
):
    """Get santri locations with score and category info."""
    where = ["sm.lokasi IS NOT NULL"]
    params: dict[str, str] = {}

    if kategori:
        where.append("sm.kategori_kemiskinan = :kategori")
        params["kategori"] = kategori

    if pesantren_id:
        where.append("sm.pesantren_id = :pesantren_id")
        params["pesantren_id"] = pesantren_id

    sql = f"""
    SELECT jsonb_build_object(
      'type','FeatureCollection',
      'features', COALESCE(
        jsonb_agg(
          jsonb_build_object(
            'type','Feature',
            'geometry', ST_AsGeoJSON(sm.lokasi)::jsonb,
            'properties', jsonb_build_object(
              'id', sm.id,
              'santri_id', sm.santri_id,
              'nama', sm.nama,
              'skor', sm.skor_terakhir,
              'ekonomi', sm.kategori_kemiskinan,
              'pesantren_id', sm.pesantren_id,
              'provinsi', sp.provinsi,
              'kabupaten', sp.kabupaten,
              'kecamatan', sp.kecamatan
            )
          )
        ), '[]'::jsonb
      )
    )
    FROM santri_map sm
    LEFT JOIN santri_pribadi sp ON sm.santri_id = sp.id
    WHERE {' AND '.join(where)};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"GIS query failed: {exc}")


@router.get("/pesantren-points")
def pesantren_points(
    provinsi: str | None = None,
    kabupaten: str | None = None,
    kecamatan: str | None = None,
    db: Session = Depends(get_db),
):
    where = ["pm.lokasi IS NOT NULL"]
    joins = []
    params: dict[str, str] = {}

    if provinsi:
        where.append("pm.provinsi = :provinsi")
        params["provinsi"] = provinsi

    if kabupaten:
        where.append("pm.kabupaten = :kabupaten")
        params["kabupaten"] = kabupaten

    sql = f"""
    SELECT jsonb_build_object(
      'type','FeatureCollection',
      'features', COALESCE(
        jsonb_agg(
          jsonb_build_object(
            'type','Feature',
            'geometry', ST_AsGeoJSON(pm.lokasi)::jsonb,
            'properties', jsonb_build_object(
              'id', pm.id,
              'pesantren_id', pm.pesantren_id,
              'nama', pm.nama,
              'nsp', pm.nsp,
              'provinsi', pm.provinsi,
              'kabupaten', pm.kabupaten,
              'skor', pm.skor_terakhir,
              'kategori', pm.kategori_kelayakan,
              'jumlah_santri', pm.jumlah_santri
            )
          )
        ), '[]'::jsonb
      )
    )
    FROM pesantren_map pm
    {' '.join(joins)}
    WHERE {' AND '.join(where)};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"GIS query failed: {exc}")

@router.get("/pesantren-heatmap")
def pesantren_heatmap(db: Session = Depends(get_db)):
    """Get pesantren heatmap with score-based intensity."""
    sql = """
    SELECT
      ST_Y(lokasi) AS lat,
      ST_X(lokasi) AS lng,
      COALESCE(skor_terakhir, 50) AS weight,
      kategori_kelayakan AS kategori,
      skor_terakhir AS skor
    FROM pesantren_map
    WHERE lokasi IS NOT NULL;
    """
    rows = db.execute(text(sql)).fetchall()

    return [
        {
            "lat": r.lat,
            "lng": r.lng,
            "weight": r.weight,
            "kategori": r.kategori,
            "skor": r.skor
        }
        for r in rows
    ]

@router.get("/heatmap")
def heatmap(
    kategori: str | None = None,
    db: Session = Depends(get_db),
):
    """Get santri heatmap with score-based intensity."""
    where = ["sm.lokasi IS NOT NULL"]
    params: dict[str, str] = {}

    if kategori:
        where.append("sm.kategori_kemiskinan = :kategori")
        params["kategori"] = kategori

    sql = f"""
    SELECT
      ST_Y(sm.lokasi) AS lat,
      ST_X(sm.lokasi) AS lng,
      COALESCE(sm.skor_terakhir, 50) AS weight,
      sm.kategori_kemiskinan AS ekonomi,
      sm.skor_terakhir AS skor
    FROM santri_map sm
    WHERE {' AND '.join(where)};
    """
    rows = db.execute(text(sql), params).fetchall()

    return [
        {
            "lat": r.lat,
            "lng": r.lng,
            "weight": r.weight,
            "ekonomi": r.ekonomi,
            "skor": r.skor
        }
        for r in rows
    ]


@router.get("/choropleth/santri-kabupaten")
def choropleth_santri_kabupaten(
    provinsi: str | None = None,
    kategori_kemiskinan: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Choropleth map data untuk santri tingkat kabupaten.
    
    Returns GeoJSON with properties:
    - total_santri: jumlah total santri di kabupaten
    - sangat_miskin: jumlah santri kategori Sangat Miskin
    - miskin: jumlah santri kategori Miskin
    - rentan: jumlah santri kategori Rentan
    - tidak_miskin: jumlah santri kategori Tidak Miskin
    - avg_skor: rata-rata skor kemiskinan
    - density: santri per km2 (jika ada data luas)
    
    Query Parameters:
    - provinsi: Filter by province name
    - kategori_kemiskinan: Filter by poverty category
    """
    where_clauses = ["k.geom IS NOT NULL"]
    params = {}
    
    if provinsi:
        where_clauses.append("k.name_1 = :provinsi")
        params["provinsi"] = provinsi
    
    if kategori_kemiskinan:
        where_clauses.append("sk.kategori_kemiskinan = :kategori")
        params["kategori"] = kategori_kemiskinan
    
    where_sql = " AND ".join(where_clauses)
    
    sql = f"""
    WITH santri_stats AS (
        SELECT 
            COALESCE(sp.kabupaten, 'Unknown') as kabupaten,
            COUNT(DISTINCT sp.id) as total_santri,
            COUNT(DISTINCT CASE WHEN sk.kategori_kemiskinan = 'Sangat Miskin' THEN sp.id END) as sangat_miskin,
            COUNT(DISTINCT CASE WHEN sk.kategori_kemiskinan = 'Miskin' THEN sp.id END) as miskin,
            COUNT(DISTINCT CASE WHEN sk.kategori_kemiskinan = 'Rentan' THEN sp.id END) as rentan,
            COUNT(DISTINCT CASE WHEN sk.kategori_kemiskinan = 'Tidak Miskin' THEN sp.id END) as tidak_miskin,
            AVG(sk.skor_total) as avg_skor
        FROM santri_pribadi sp
        LEFT JOIN santri_skor sk ON sp.id = sk.santri_id
        WHERE sp.kabupaten IS NOT NULL
        GROUP BY sp.kabupaten
    )
    SELECT jsonb_build_object(
        'type', 'FeatureCollection',
        'features', COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(k.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'kabupaten', k.name_2,
                        'provinsi', k.name_1,
                        'total_santri', COALESCE(ss.total_santri, 0),
                        'sangat_miskin', COALESCE(ss.sangat_miskin, 0),
                        'miskin', COALESCE(ss.miskin, 0),
                        'rentan', COALESCE(ss.rentan, 0),
                        'tidak_miskin', COALESCE(ss.tidak_miskin, 0),
                        'avg_skor', ROUND(COALESCE(ss.avg_skor, 0)::numeric, 2),
                        'pct_sangat_miskin', ROUND(
                            CASE WHEN ss.total_santri > 0 
                            THEN (ss.sangat_miskin::float / ss.total_santri * 100)
                            ELSE 0 END::numeric, 2
                        ),
                        'pct_miskin', ROUND(
                            CASE WHEN ss.total_santri > 0 
                            THEN (ss.miskin::float / ss.total_santri * 100)
                            ELSE 0 END::numeric, 2
                        )
                    )
                )
            ), '[]'::jsonb
        )
    )
    FROM {_tbl(KAB_TABLE)} k
    LEFT JOIN santri_stats ss ON k.name_2 = ss.kabupaten
    WHERE {where_sql};
    """
    
    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Choropleth query failed: {exc}")


@router.get("/choropleth/pesantren-kabupaten")
def choropleth_pesantren_kabupaten(
    provinsi: str | None = None,
    kategori_kelayakan: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Choropleth map data untuk pesantren tingkat kabupaten.
    
    Returns GeoJSON with properties:
    - total_pesantren: jumlah total pesantren di kabupaten
    - sangat_layak: jumlah pesantren kategori Sangat Layak
    - layak: jumlah pesantren kategori Layak
    - cukup_layak: jumlah pesantren kategori Cukup Layak
    - kurang_layak: jumlah pesantren kategori Kurang Layak
    - avg_skor: rata-rata skor kelayakan
    - total_santri_pesantren: total santri di semua pesantren
    
    Query Parameters:
    - provinsi: Filter by province name
    - kategori_kelayakan: Filter by eligibility category
    """
    where_clauses = ["k.geom IS NOT NULL"]
    params = {}
    
    if provinsi:
        where_clauses.append("k.name_1 = :provinsi")
        params["provinsi"] = provinsi
    
    if kategori_kelayakan:
        where_clauses.append("ps.kategori_kelayakan = :kategori")
        params["kategori"] = kategori_kelayakan
    
    where_sql = " AND ".join(where_clauses)
    
    sql = f"""
    WITH pesantren_stats AS (
        SELECT 
            COALESCE(pp.kabupaten, 'Unknown') as kabupaten,
            COUNT(DISTINCT pp.id) as total_pesantren,
            COUNT(DISTINCT CASE WHEN ps.kategori_kelayakan = 'Sangat Layak' THEN pp.id END) as sangat_layak,
            COUNT(DISTINCT CASE WHEN ps.kategori_kelayakan = 'Layak' THEN pp.id END) as layak,
            COUNT(DISTINCT CASE WHEN ps.kategori_kelayakan = 'Cukup Layak' THEN pp.id END) as cukup_layak,
            COUNT(DISTINCT CASE WHEN ps.kategori_kelayakan = 'Kurang Layak' THEN pp.id END) as kurang_layak,
            AVG(ps.skor_total) as avg_skor,
            SUM(pp.jumlah_santri) as total_santri_pesantren
        FROM pondok_pesantren pp
        LEFT JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
        WHERE pp.kabupaten IS NOT NULL
        GROUP BY pp.kabupaten
    )
    SELECT jsonb_build_object(
        'type', 'FeatureCollection',
        'features', COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(k.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'kabupaten', k.name_2,
                        'provinsi', k.name_1,
                        'total_pesantren', COALESCE(ps.total_pesantren, 0),
                        'sangat_layak', COALESCE(ps.sangat_layak, 0),
                        'layak', COALESCE(ps.layak, 0),
                        'cukup_layak', COALESCE(ps.cukup_layak, 0),
                        'kurang_layak', COALESCE(ps.kurang_layak, 0),
                        'avg_skor', ROUND(COALESCE(ps.avg_skor, 0)::numeric, 2),
                        'total_santri_pesantren', COALESCE(ps.total_santri_pesantren, 0),
                        'pct_sangat_layak', ROUND(
                            CASE WHEN ps.total_pesantren > 0 
                            THEN (ps.sangat_layak::float / ps.total_pesantren * 100)
                            ELSE 0 END::numeric, 2
                        ),
                        'pct_layak', ROUND(
                            CASE WHEN ps.total_pesantren > 0 
                            THEN (ps.layak::float / ps.total_pesantren * 100)
                            ELSE 0 END::numeric, 2
                        )
                    )
                )
            ), '[]'::jsonb
        )
    )
    FROM {_tbl(KAB_TABLE)} k
    LEFT JOIN pesantren_stats ps ON k.name_2 = ps.kabupaten
    WHERE {where_sql};
    """
    
    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Choropleth query failed: {exc}")


@router.get("/choropleth/stats")
def choropleth_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics for choropleth visualization options.
    
    Returns:
    - santri_categories: Available poverty categories with counts
    - pesantren_categories: Available eligibility categories with counts
    - kabupaten_list: List of kabupaten with data
    - provinsi_list: List of provinces with data
    """
    sql = """
    SELECT jsonb_build_object(
        'santri_categories', (
            SELECT jsonb_agg(jsonb_build_object(
                'kategori', kategori_kemiskinan,
                'count', count
            ))
            FROM (
                SELECT 
                    COALESCE(kategori_kemiskinan, 'No Data') as kategori_kemiskinan,
                    COUNT(*) as count
                FROM santri_skor
                GROUP BY kategori_kemiskinan
                ORDER BY count DESC
            ) cat
        ),
        'pesantren_categories', (
            SELECT jsonb_agg(jsonb_build_object(
                'kategori', kategori_kelayakan,
                'count', count
            ))
            FROM (
                SELECT 
                    COALESCE(kategori_kelayakan, 'No Data') as kategori_kelayakan,
                    COUNT(*) as count
                FROM pesantren_skor
                GROUP BY kategori_kelayakan
                ORDER BY count DESC
            ) cat
        ),
        'kabupaten_list', (
            SELECT jsonb_agg(DISTINCT kabupaten ORDER BY kabupaten)
            FROM (
                SELECT kabupaten FROM santri_pribadi WHERE kabupaten IS NOT NULL
                UNION
                SELECT kabupaten FROM pondok_pesantren WHERE kabupaten IS NOT NULL
            ) kab
        ),
        'provinsi_list', (
            SELECT jsonb_agg(DISTINCT provinsi ORDER BY provinsi)
            FROM (
                SELECT provinsi FROM santri_pribadi WHERE provinsi IS NOT NULL
                UNION
                SELECT provinsi FROM pondok_pesantren WHERE provinsi IS NOT NULL
            ) prov
        )
    );
    """
    
    try:
        return db.execute(text(sql)).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stats query failed: {exc}")
