"""
Import Indonesian administrative boundaries (provinsi, kabupaten, kecamatan) from GeoJSON
into PostGIS tables: public.provinsi, public.kabupaten, public.kecamatan

- Geometry stored as MultiPolygon SRID 4326
- Creates GIST index on geom and BTree indexes on name columns
- Reads DATABASE_URL from .env or environment; fallback to common local setup

Usage:
    python -m app.gis.import_admin_boundaries
"""
import os
import json
from pathlib import Path
from typing import Optional

import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

# Resolve database URL with sensible fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:admin@localhost:5433/santri_db",
)

DATA_DIR = Path(__file__).parent / "data"
FILES = {
    "provinsi": DATA_DIR / "indonesia-provinsi.geojson",
    "kabupaten": DATA_DIR / "indonesia-kabupaten.geojson",
    "kecamatan": DATA_DIR / "indonesia-kecamatan.geojson",
}

SCHEMA = "public"

TABLE_SQL = {
    "provinsi": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.provinsi (
            id SERIAL PRIMARY KEY,
            name_1 TEXT NOT NULL,
            geom geometry(MultiPolygon, 4326) NOT NULL
        );
    """,
    "kabupaten": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.kabupaten (
            id SERIAL PRIMARY KEY,
            name_1 TEXT NOT NULL,
            name_2 TEXT NOT NULL,
            geom geometry(MultiPolygon, 4326) NOT NULL
        );
    """,
    "kecamatan": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.kecamatan (
            id SERIAL PRIMARY KEY,
            name_1 TEXT NOT NULL,
            name_2 TEXT NOT NULL,
            name_3 TEXT NOT NULL,
            geom geometry(MultiPolygon, 4326) NOT NULL
        );
    """,
}

INDEX_SQL = {
    "provinsi": [
        f"CREATE INDEX IF NOT EXISTS idx_provinsi_geom ON {SCHEMA}.provinsi USING GIST (geom)",
        f"CREATE INDEX IF NOT EXISTS idx_provinsi_name1 ON {SCHEMA}.provinsi (name_1)",
    ],
    "kabupaten": [
        f"CREATE INDEX IF NOT EXISTS idx_kabupaten_geom ON {SCHEMA}.kabupaten USING GIST (geom)",
        f"CREATE INDEX IF NOT EXISTS idx_kabupaten_name1 ON {SCHEMA}.kabupaten (name_1)",
        f"CREATE INDEX IF NOT EXISTS idx_kabupaten_name2 ON {SCHEMA}.kabupaten (name_2)",
    ],
    "kecamatan": [
        f"CREATE INDEX IF NOT EXISTS idx_kecamatan_geom ON {SCHEMA}.kecamatan USING GIST (geom)",
        f"CREATE INDEX IF NOT EXISTS idx_kecamatan_name2 ON {SCHEMA}.kecamatan (name_2)",
        f"CREATE INDEX IF NOT EXISTS idx_kecamatan_name3 ON {SCHEMA}.kecamatan (name_3)",
    ],
}

def get_conn():
    return psycopg2.connect(DATABASE_URL)


def load_geojson(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def clear_table(conn, table: str):
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {SCHEMA}.{table}")
    conn.commit()


def upsert_admin_table(conn, table: str, features: list[dict]):
    """Insert features into table using ST_GeomFromGeoJSON -> ST_SetSRID -> ST_Multi"""
    # Map of property names per level
    if table == "provinsi":
        def make_row(feat):
            props = feat.get("properties", {})
            name_1 = props.get("NAME_1") or props.get("name_1") or props.get("provinsi") or "Unknown"
            geom = json.dumps(feat.get("geometry"))
            return (name_1, geom)
        insert_sql = f"""
            INSERT INTO {SCHEMA}.provinsi (name_1, geom)
            VALUES (%s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)))
        """
    elif table == "kabupaten":
        def make_row(feat):
            props = feat.get("properties", {})
            name_1 = props.get("NAME_1") or props.get("name_1") or "Unknown"
            name_2 = props.get("NAME_2") or props.get("name_2") or props.get("kabupaten") or "Unknown"
            geom = json.dumps(feat.get("geometry"))
            return (name_1, name_2, geom)
        insert_sql = f"""
            INSERT INTO {SCHEMA}.kabupaten (name_1, name_2, geom)
            VALUES (%s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)))
        """
    elif table == "kecamatan":
        def make_row(feat):
            props = feat.get("properties", {})
            name_1 = props.get("NAME_1") or props.get("name_1") or "Unknown"
            name_2 = props.get("NAME_2") or props.get("name_2") or "Unknown"
            name_3 = props.get("NAME_3") or props.get("name_3") or props.get("kecamatan") or "Unknown"
            geom = json.dumps(feat.get("geometry"))
            return (name_1, name_2, name_3, geom)
        insert_sql = f"""
            INSERT INTO {SCHEMA}.kecamatan (name_1, name_2, name_3, geom)
            VALUES (%s, %s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)))
        """
    else:
        raise ValueError(f"Unknown table: {table}")

    rows = [make_row(f) for f in features]
    with conn.cursor() as cur:
        execute_batch(cur, insert_sql, rows, page_size=500)
    conn.commit()


def ensure_tables(conn):
    with conn.cursor() as cur:
        for t, sql in TABLE_SQL.items():
            cur.execute(sql)
    conn.commit()
    # Indexes
    with conn.cursor() as cur:
        for t, idx_list in INDEX_SQL.items():
            for idx_sql in idx_list:
                cur.execute(idx_sql)
    conn.commit()


def import_all():
    conn = get_conn()
    ensure_tables(conn)

    completed = []
    for level, path in FILES.items():
        gj = load_geojson(path)
        if gj is None:
            print(f"⚠️  Missing file: {path}")
            continue
        features = gj.get("features", [])
        if not features:
            print(f"⚠️  No features in: {path}")
            continue
        print(f"➡️  Importing {level} ({len(features)} features) from {path}")
        clear_table(conn, level)
        upsert_admin_table(conn, level, features)
        print(f"✅ Imported {level}")
        completed.append(level)

    conn.close()
    print(f"\nDone. Imported: {', '.join(completed) if completed else 'none'}")


if __name__ == "__main__":
    import_all()
