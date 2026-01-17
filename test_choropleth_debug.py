"""Debug choropleth endpoint SQL"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/santri_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_santri_choropleth():
    db = SessionLocal()
    
    # The exact SQL from the endpoint
    cte_where = "sp.kabupaten IS NOT NULL"
    where_sql = "k.geom IS NOT NULL"
    
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
    FROM idn_admbnda_adm2_bps_20200401 k
    LEFT JOIN santri_stats ss ON k.name_2 = ss.kabupaten
    WHERE {where_sql};
    """
    
    try:
        result = db.execute(text(sql))
        print("✓ Query executed successfully")
        data = result.scalar()
        print(f"✓ Result type: {type(data)}")
        return data
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing santri-kabupaten choropleth query...")
    test_santri_choropleth()
