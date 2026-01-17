"""
Create and refresh materialized views for choropleth stats.

Views:
- mv_santri_stats_kabupaten
- mv_pesantren_stats_kabupaten

Run:
    python -m app.gis.create_materialized_views
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5433/santri_db")

def ensure_materialized_views():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        # Santri MV
        conn.execute(text(
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_santri_stats_kabupaten AS
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
            WHERE sp.kabupaten IS NOT NULL
            GROUP BY sp.kabupaten;
            """
        ))
        conn.execute(text("CREATE INDEX IF NOT EXISTS mv_santri_stats_kabupaten_kab_idx ON mv_santri_stats_kabupaten (kabupaten)"))

        # Pesantren MV
        conn.execute(text(
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_pesantren_stats_kabupaten AS
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
            WHERE pp.kabupaten IS NOT NULL
            GROUP BY pp.kabupaten;
            """
        ))
        conn.execute(text("CREATE INDEX IF NOT EXISTS mv_pesantren_stats_kabupaten_kab_idx ON mv_pesantren_stats_kabupaten (kabupaten)"))


def refresh_materialized_views():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW mv_santri_stats_kabupaten"))
        conn.execute(text("REFRESH MATERIALIZED VIEW mv_pesantren_stats_kabupaten"))


if __name__ == "__main__":
    ensure_materialized_views()
    refresh_materialized_views()
    print("Materialized views created/refreshed: mv_santri_stats_kabupaten, mv_pesantren_stats_kabupaten")
