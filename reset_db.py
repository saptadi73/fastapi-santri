#!/usr/bin/env python3
"""Reset database by dropping all tables and schema."""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost:5433/santri_db')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Drop ALL tables in public schema with CASCADE (excluding PostGIS managed ones)
    cursor.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns')) LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
    # Drop ALL enum types in public schema
    cursor.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT typname FROM pg_type WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public') AND typtype = 'e') LOOP
                EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
    conn.commit()
    print("✅ Database reset successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
