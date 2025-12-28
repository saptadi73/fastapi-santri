#!/usr/bin/env python3
"""Check database schema."""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost:5433/santri_db')

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Check all tables
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    print("=== TABLES ===")
    for row in cursor.fetchall():
        print(f"  {row[0]}")
    
    # Check all indexes
    cursor.execute("""
        SELECT indexname FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY indexname
    """)
    print("\n=== INDEXES ===")
    for row in cursor.fetchall():
        print(f"  {row[0]}")
    
    # Check all types
    cursor.execute("""
        SELECT typname FROM pg_type 
        WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        ORDER BY typname
    """)
    print("\n=== TYPES ===")
    for row in cursor.fetchall():
        print(f"  {row[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
