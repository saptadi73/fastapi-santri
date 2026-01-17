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

def _mv_exists(db: Session, name: str) -> bool:
    """Check if a materialized view or table exists by regclass lookup."""
    try:
        exists = db.execute(text("SELECT to_regclass(:name) IS NOT NULL"), {"name": name}).scalar()
        return bool(exists)
    except Exception:
        return False


@router.get("/santri-points")
def santri_points(
    kategori: str | None = None,
    pesantren_id: str | None = None,
    page: int = 1,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """Get santri locations with score and category info (paginated)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 5000:
        limit = 1000
    
    where = ["sm.lokasi IS NOT NULL"]
    params: dict = {}

    if kategori:
        where.append("sm.kategori_kemiskinan = :kategori")
        params["kategori"] = kategori

    if pesantren_id:
        where.append("sm.pesantren_id = :pesantren_id")
        params["pesantren_id"] = pesantren_id

    offset = (page - 1) * limit
    where_sql = " AND ".join(where)
    
    # Get total count (cached query, lightweight)
    count_sql = f"SELECT COUNT(*) FROM santri_map sm WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar()

    # Get paginated data (optimized - no JOIN, no ST_AsGeoJSON aggregation)
    sql = f"""
    SELECT 
        sm.id,
        sm.santri_id,
        sm.nama,
        ST_Y(sm.lokasi) as lat,
        ST_X(sm.lokasi) as lng,
        sm.skor_terakhir,
        sm.kategori_kemiskinan,
        sm.pesantren_id
    FROM santri_map sm
    WHERE {where_sql}
    ORDER BY sm.id
    LIMIT :limit OFFSET :offset
    """
    
    params['limit'] = limit
    params['offset'] = offset
    
    rows = db.execute(text(sql), params).fetchall()

    # Format GeoJSON di Python (lebih efisien)
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.lng, row.lat]
            },
            "properties": {
                "id": row.id,
                "santri_id": row.santri_id,
                "nama": row.nama,
                "skor": row.skor_terakhir,
                "ekonomi": row.kategori_kemiskinan,
                "pesantren_id": row.pesantren_id
            }
        }
        for row in rows
    ]

    return {
        "type": "FeatureCollection",
        "features": features,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total or 0,
            "pages": ((total or 0) + limit - 1) // limit
        }
    }

    try:
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"GIS query failed: {exc}")


@router.get("/pesantren-points")
def pesantren_points(
    provinsi: str | None = None,
    kabupaten: str | None = None,
    page: int = 1,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """Get pesantren locations with details (paginated)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 5000:
        limit = 1000
    
    where = ["pm.lokasi IS NOT NULL"]
    params: dict = {}

    if provinsi:
        where.append("pm.provinsi = :provinsi")
        params["provinsi"] = provinsi

    if kabupaten:
        where.append("pm.kabupaten = :kabupaten")
        params["kabupaten"] = kabupaten
    

    offset = (page - 1) * limit
    where_sql = " AND ".join(where)
    
    # Get total count
    count_sql = f"SELECT COUNT(*) FROM pesantren_map pm WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar()

    # Get paginated data (optimized)
    sql = f"""
    SELECT 
        pm.id,
        pm.pesantren_id,
        pm.nama,
        pm.nsp,
        ST_Y(pm.lokasi) as lat,
        ST_X(pm.lokasi) as lng,
        pm.skor_terakhir,
        pm.kategori_kelayakan,
        pm.jumlah_santri,
        pm.provinsi,
        pm.kabupaten
    FROM pesantren_map pm
    WHERE {where_sql}
    ORDER BY pm.id
    LIMIT :limit OFFSET :offset
    """
    
    params['limit'] = limit
    params['offset'] = offset

    rows = db.execute(text(sql), params).fetchall()

    # Format GeoJSON di Python
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.lng, row.lat]
            },
            "properties": {
                "id": row.id,
                "pesantren_id": row.pesantren_id,
                "nama": row.nama,
                "nsp": row.nsp,
                "skor": row.skor_terakhir,
                "kategori": row.kategori_kelayakan,
                "jumlah_santri": row.jumlah_santri,
                "provinsi": row.provinsi,
                "kabupaten": row.kabupaten
            }
        }
        for row in rows
    ]

    return {
        "type": "FeatureCollection",
        "features": features,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total or 0,
            "pages": ((total or 0) + limit - 1) // limit
        }
    }

@router.get("/pesantren-heatmap")
def pesantren_heatmap(
    page: int = 1,
    limit: int = 5000,
    db: Session = Depends(get_db)
):
    """Get pesantren heatmap with score-based intensity (paginated)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 10000:
        limit = 5000
    
    offset = (page - 1) * limit
    
    # Lightweight query - no aggregation
    count_sql = "SELECT COUNT(*) FROM pesantren_map WHERE lokasi IS NOT NULL"
    total = db.execute(text(count_sql)).scalar()
    
    sql = """
    SELECT
      ST_Y(lokasi) AS lat,
      ST_X(lokasi) AS lng,
      COALESCE(skor_terakhir, 50) AS weight,
      kategori_kelayakan AS kategori,
      skor_terakhir AS skor,
      id
    FROM pesantren_map
    WHERE lokasi IS NOT NULL
    ORDER BY id
    LIMIT :limit OFFSET :offset
    """
    
    rows = db.execute(text(sql), {"limit": limit, "offset": offset}).fetchall()

    return {
        "data": [
            {
                "lat": r.lat,
                "lng": r.lng,
                "weight": float(r.weight),
                "kategori": r.kategori,
                "skor": r.skor,
                "id": r.id
            }
            for r in rows
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total or 0,
            "pages": ((total or 0) + limit - 1) // limit
        }
    }

@router.get("/heatmap")
def heatmap(
    kategori: str | None = None,
    page: int = 1,
    limit: int = 5000,
    db: Session = Depends(get_db),
):
    """Get santri heatmap with score-based intensity (paginated)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 10000:
        limit = 5000
    
    where = ["sm.lokasi IS NOT NULL"]
    params: dict = {}

    if kategori:
        where.append("sm.kategori_kemiskinan = :kategori")
        params["kategori"] = kategori

    offset = (page - 1) * limit
    where_sql = " AND ".join(where)
    
    # Count query with alias
    count_sql = f"SELECT COUNT(*) FROM santri_map sm WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar()

    sql = f"""
    SELECT
      ST_Y(sm.lokasi) AS lat,
      ST_X(sm.lokasi) AS lng,
      COALESCE(sm.skor_terakhir, 50) AS weight,
      sm.kategori_kemiskinan AS ekonomi,
      sm.skor_terakhir AS skor,
      sm.id
    FROM santri_map sm
    WHERE {where_sql}
    ORDER BY sm.id
    LIMIT :limit OFFSET :offset
    """
    
    params['limit'] = limit
    params['offset'] = offset
    
    rows = db.execute(text(sql), params).fetchall()

    return {
        "data": [
            {
                "lat": r.lat,
                "lng": r.lng,
                "weight": float(r.weight),
                "ekonomi": r.ekonomi,
                "skor": r.skor,
                "id": r.id
            }
            for r in rows
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total or 0,
            "pages": ((total or 0) + limit - 1) // limit
        }
    }


@router.get("/choropleth/santri-kabupaten")
def choropleth_santri_kabupaten(
    provinsi: str | None = None,
    kategori_kemiskinan: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Choropleth map data untuk santri tingkat kabupaten.
    Requires admin boundary table to be loaded.
    """
    # Check if boundary table exists
    try:
        db.execute(text(f"SELECT 1 FROM {_tbl(KAB_TABLE)} LIMIT 1"))
    except Exception:
        raise HTTPException(
            status_code=501,
            detail=f"Admin boundary table '{_tbl(KAB_TABLE)}' not found. Please import Indonesian admin boundaries (e.g., from BPS or GADM) to enable choropleth maps."
        )
    
    where_clauses = ["k.geom IS NOT NULL"]
    params = {}
    
    if provinsi:
        where_clauses.append("k.name_1 = :provinsi")
        params["provinsi"] = provinsi
    
    # kategori_kemiskinan filtering is done in the CTE aggregation, not in WHERE clause
    where_sql = " AND ".join(where_clauses)
    
    # Build CTE WHERE clause for santri filtering
    cte_where = "sp.kabupaten IS NOT NULL"
    if kategori_kemiskinan:
        cte_where += " AND sk.kategori_kemiskinan = :kategori"
        params["kategori"] = kategori_kemiskinan
    
    use_mv = _mv_exists(db, "mv_santri_stats_kabupaten")
    if use_mv:
        sql = f"""
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
                            'avg_skor', COALESCE(ss.avg_skor, 0),
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
        LEFT JOIN mv_santri_stats_kabupaten ss ON k.name_2 = ss.kabupaten
        WHERE {where_sql};
        """
    else:
        # Optimized: FILTER clause instead of multiple COUNT DISTINCT CASE
        sql = f"""
        WITH santri_stats AS (
            SELECT 
                COALESCE(sp.kabupaten, 'Unknown') as kabupaten,
                COUNT(DISTINCT sp.id) as total_santri,
                COUNT(DISTINCT sp.id) FILTER (WHERE sk.kategori_kemiskinan = 'Sangat Miskin') as sangat_miskin,
                COUNT(DISTINCT sp.id) FILTER (WHERE sk.kategori_kemiskinan = 'Miskin') as miskin,
                COUNT(DISTINCT sp.id) FILTER (WHERE sk.kategori_kemiskinan = 'Rentan') as rentan,
                COUNT(DISTINCT sp.id) FILTER (WHERE sk.kategori_kemiskinan = 'Tidak Miskin') as tidak_miskin,
                ROUND(AVG(sk.skor_total)::numeric, 2) as avg_skor
            FROM santri_pribadi sp
            LEFT JOIN santri_skor sk ON sp.id = sk.santri_id
            WHERE {cte_where}
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
                            'avg_skor', COALESCE(ss.avg_skor, 0),
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
    Requires admin boundary table to be loaded.
    """
    # Check if boundary table exists
    try:
        db.execute(text(f"SELECT 1 FROM {_tbl(KAB_TABLE)} LIMIT 1"))
    except Exception:
        raise HTTPException(
            status_code=501,
            detail=f"Admin boundary table '{_tbl(KAB_TABLE)}' not found. Please import Indonesian admin boundaries (e.g., from BPS or GADM) to enable choropleth maps."
        )
    
    where_clauses = ["k.geom IS NOT NULL"]
    params = {}
    
    if provinsi:
        where_clauses.append("k.name_1 = :provinsi")
        params["provinsi"] = provinsi
    
    # kategori_kelayakan filtering is done in the CTE aggregation, not in WHERE clause
    where_sql = " AND ".join(where_clauses)
    
    # Build CTE WHERE clause for pesantren filtering
    cte_where = "pp.kabupaten IS NOT NULL"
    if kategori_kelayakan:
        cte_where += " AND ps.kategori_kelayakan = :kategori"
        params["kategori"] = kategori_kelayakan
    
    use_mv = _mv_exists(db, "mv_pesantren_stats_kabupaten")
    if use_mv:
        sql = f"""
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
                            'avg_skor', COALESCE(ps.avg_skor, 0),
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
        LEFT JOIN mv_pesantren_stats_kabupaten ps ON k.name_2 = ps.kabupaten
        WHERE {where_sql};
        """
    else:
        # Optimized: FILTER clause instead of multiple COUNT DISTINCT CASE
        sql = f"""
        WITH pesantren_stats AS (
            SELECT 
                COALESCE(pp.kabupaten, 'Unknown') as kabupaten,
                COUNT(DISTINCT pp.id) as total_pesantren,
                COUNT(DISTINCT pp.id) FILTER (WHERE ps.kategori_kelayakan = 'Sangat Layak') as sangat_layak,
                COUNT(DISTINCT pp.id) FILTER (WHERE ps.kategori_kelayakan = 'Layak') as layak,
                COUNT(DISTINCT pp.id) FILTER (WHERE ps.kategori_kelayakan = 'Cukup Layak') as cukup_layak,
                COUNT(DISTINCT pp.id) FILTER (WHERE ps.kategori_kelayakan = 'Kurang Layak') as kurang_layak,
                ROUND(AVG(ps.skor_total)::numeric, 2) as avg_skor,
                COALESCE(SUM(pp.jumlah_santri), 0) as total_santri_pesantren
            FROM pondok_pesantren pp
            LEFT JOIN pesantren_skor ps ON pp.id = ps.pesantren_id
            WHERE {cte_where}
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
                            'avg_skor', COALESCE(ps.avg_skor, 0),
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

@router.post("/choropleth/refresh")
def refresh_choropleth_views(db: Session = Depends(get_db)):
    """Refresh materialized views if available."""
    refreshed = []
    try:
        if _mv_exists(db, "mv_santri_stats_kabupaten"):
            db.execute(text("REFRESH MATERIALIZED VIEW mv_santri_stats_kabupaten"))
            refreshed.append("mv_santri_stats_kabupaten")
        if _mv_exists(db, "mv_pesantren_stats_kabupaten"):
            db.execute(text("REFRESH MATERIALIZED VIEW mv_pesantren_stats_kabupaten"))
            refreshed.append("mv_pesantren_stats_kabupaten")
        return {"refreshed": refreshed}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {exc}")
    
    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Choropleth query failed: {exc}")


# --- Admin boundaries preview endpoints ---
@router.get("/boundaries/provinsi")
def boundaries_provinsi(
    provinsi: str | None = None,
    db: Session = Depends(get_db),
):
    """Return provinsi boundaries as GeoJSON FeatureCollection."""
    where = ["p.geom IS NOT NULL"]
    params: dict[str, str] = {}
    if provinsi:
        where.append("p.name_1 = :provinsi")
        params["provinsi"] = provinsi
    where_sql = " AND ".join(where)

    sql = f"""
    SELECT jsonb_build_object(
        'type','FeatureCollection',
        'features', COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(p.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'provinsi', p.name_1
                    )
                )
            ), '[]'::jsonb
        )
    )
    FROM {_tbl(PROV_TABLE)} p
    WHERE {where_sql};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Boundaries query failed: {exc}")


@router.get("/boundaries/kabupaten")
def boundaries_kabupaten(
    provinsi: str | None = None,
    kabupaten: str | None = None,
    db: Session = Depends(get_db),
):
    """Return kabupaten boundaries as GeoJSON FeatureCollection (optional filters)."""
    where = ["k.geom IS NOT NULL"]
    params: dict[str, str] = {}
    if provinsi:
        where.append("k.name_1 = :provinsi")
        params["provinsi"] = provinsi
    if kabupaten:
        where.append("k.name_2 = :kabupaten")
        params["kabupaten"] = kabupaten
    where_sql = " AND ".join(where)

    sql = f"""
    SELECT jsonb_build_object(
        'type','FeatureCollection',
        'features', COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(k.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'provinsi', k.name_1,
                        'kabupaten', k.name_2
                    )
                )
            ), '[]'::jsonb
        )
    )
    FROM {_tbl(KAB_TABLE)} k
    WHERE {where_sql};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Boundaries query failed: {exc}")


@router.get("/boundaries/kecamatan")
def boundaries_kecamatan(
    provinsi: str | None = None,
    kabupaten: str | None = None,
    kecamatan: str | None = None,
    db: Session = Depends(get_db),
):
    """Return kecamatan boundaries as GeoJSON FeatureCollection (optional filters)."""
    where = ["c.geom IS NOT NULL"]
    params: dict[str, str] = {}
    if provinsi:
        where.append("c.name_1 = :provinsi")
        params["provinsi"] = provinsi
    if kabupaten:
        where.append("c.name_2 = :kabupaten")
        params["kabupaten"] = kabupaten
    if kecamatan:
        where.append("c.name_3 = :kecamatan")
        params["kecamatan"] = kecamatan
    where_sql = " AND ".join(where)

    sql = f"""
    SELECT jsonb_build_object(
        'type','FeatureCollection',
        'features', COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(c.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'provinsi', c.name_1,
                        'kabupaten', c.name_2,
                        'kecamatan', c.name_3
                    )
                )
            ), '[]'::jsonb
        )
    )
    FROM {_tbl(KEC_TABLE)} c
    WHERE {where_sql};
    """

    try:
        return db.execute(text(sql), params).scalar()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Boundaries query failed: {exc}")


@router.get("/choropleth/stats")
def choropleth_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics for choropleth visualization options.
    Optimized: reduced sub-queries, uses UNION ALL
    
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
            ) ORDER BY count DESC)
            FROM (
                SELECT 
                    COALESCE(kategori_kemiskinan, 'No Data') as kategori_kemiskinan,
                    COUNT(*) as count
                FROM santri_skor
                WHERE kategori_kemiskinan IS NOT NULL
                GROUP BY kategori_kemiskinan
            ) cat
        ),
        'pesantren_categories', (
            SELECT jsonb_agg(jsonb_build_object(
                'kategori', kategori_kelayakan,
                'count', count
            ) ORDER BY count DESC)
            FROM (
                SELECT 
                    COALESCE(kategori_kelayakan, 'No Data') as kategori_kelayakan,
                    COUNT(*) as count
                FROM pesantren_skor
                WHERE kategori_kelayakan IS NOT NULL
                GROUP BY kategori_kelayakan
            ) cat
        ),
        'kabupaten_list', (
            SELECT jsonb_agg(DISTINCT kabupaten ORDER BY kabupaten)
            FROM (
                SELECT kabupaten FROM santri_pribadi WHERE kabupaten IS NOT NULL
                UNION ALL
                SELECT kabupaten FROM pondok_pesantren WHERE kabupaten IS NOT NULL
            ) kab
        ),
        'provinsi_list', (
            SELECT jsonb_agg(DISTINCT provinsi ORDER BY provinsi)
            FROM (
                SELECT provinsi FROM santri_pribadi WHERE provinsi IS NOT NULL
                UNION ALL
                SELECT provinsi FROM pondok_pesantren WHERE provinsi IS NOT NULL
            ) prov
        )
    );
    """
    
    try:
        result = db.execute(text(sql)).scalar()
        return result if result else {}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stats query failed: {exc}")
