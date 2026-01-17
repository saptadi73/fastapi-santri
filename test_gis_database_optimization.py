"""
Test GIS Database Optimization
Script untuk check dan implement optimasi database sesuai rekomendasi
"""
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Parse DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
# postgresql://postgres:admin@localhost:5433/santri_db

def get_connection():
    """Get database connection from DATABASE_URL"""
    return psycopg2.connect(DATABASE_URL)

def check_existing_indexes(conn):
    """Check existing indexes in the database"""
    print("\n" + "="*80)
    print("📊 CHECKING EXISTING INDEXES")
    print("="*80)
    
    cursor = conn.cursor()
    
    # Check GIS-related indexes
    query = """
    SELECT 
        schemaname,
        tablename, 
        indexname,
        indexdef
    FROM pg_indexes
    WHERE tablename IN ('santri_map', 'pesantren_map', 'santri_pribadi', 
                        'pondok_pesantren', 'santri_skor', 'pesantren_skor')
    ORDER BY tablename, indexname;
    """
    
    cursor.execute(query)
    indexes = cursor.fetchall()
    
    if indexes:
        current_table = None
        for schema, table, index_name, index_def in indexes:
            if current_table != table:
                print(f"\n📋 Table: {table}")
                current_table = table
            print(f"  ✓ {index_name}")
            print(f"    {index_def}")
    else:
        print("⚠️  No indexes found!")
    
    cursor.close()
    return indexes

def check_table_sizes(conn):
    """Check table sizes and row counts"""
    print("\n" + "="*80)
    print("📏 TABLE SIZES & ROW COUNTS")
    print("="*80)
    
    cursor = conn.cursor()
    
    tables = ['santri_map', 'pesantren_map', 'santri_pribadi', 
              'pondok_pesantren', 'santri_skor', 'pesantren_skor']
    
    for table in tables:
        try:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # Get table size
            cursor.execute(f"""
                SELECT pg_size_pretty(pg_total_relation_size('{table}'))
            """)
            size = cursor.fetchone()[0]
            
            print(f"📊 {table:25} | Rows: {count:>10,} | Size: {size}")
        except Exception as e:
            print(f"❌ {table:25} | Error: {str(e)}")
    
    cursor.close()

def check_spatial_columns(conn):
    """Check if spatial columns exist and have proper types"""
    print("\n" + "="*80)
    print("🗺️  CHECKING SPATIAL COLUMNS")
    print("="*80)
    
    cursor = conn.cursor()
    
    # Check santri_map
    try:
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'santri_map' AND column_name = 'lokasi'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✓ santri_map.lokasi: {result[1]} ({result[2]})")
        else:
            print("⚠️  santri_map.lokasi NOT FOUND")
    except Exception as e:
        print(f"❌ Error checking santri_map: {e}")
    
    # Check pesantren_map
    try:
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'pesantren_map' AND column_name = 'lokasi'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✓ pesantren_map.lokasi: {result[1]} ({result[2]})")
        else:
            print("⚠️  pesantren_map.lokasi NOT FOUND")
    except Exception as e:
        print(f"❌ Error checking pesantren_map: {e}")
    
    cursor.close()

def create_optimization_indexes(conn, dry_run=True):
    """Create recommended indexes for optimization"""
    print("\n" + "="*80)
    print("🔧 CREATING OPTIMIZATION INDEXES")
    print("="*80)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No indexes will be created")
    
    cursor = conn.cursor()
    
    # List of indexes to create
    indexes_sql = [
        # GIST Spatial Indexes
        ("idx_santri_map_lokasi", """
            CREATE INDEX IF NOT EXISTS idx_santri_map_lokasi 
            ON santri_map USING GIST(lokasi) 
            WHERE lokasi IS NOT NULL
        """),
        
        ("idx_pesantren_map_lokasi", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_map_lokasi 
            ON pesantren_map USING GIST(lokasi) 
            WHERE lokasi IS NOT NULL
        """),
        
        # Filter columns
        ("idx_santri_map_kategori", """
            CREATE INDEX IF NOT EXISTS idx_santri_map_kategori 
            ON santri_map(kategori_kemiskinan)
        """),
        
        ("idx_santri_map_skor", """
            CREATE INDEX IF NOT EXISTS idx_santri_map_skor 
            ON santri_map(skor_terakhir)
        """),
        
        ("idx_pesantren_map_kategori", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_map_kategori 
            ON pesantren_map(kategori_kelayakan)
        """),
        
        ("idx_pesantren_map_skor", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_map_skor 
            ON pesantren_map(skor_terakhir)
        """),
        
        # Join optimization
        ("idx_santri_map_santri_id", """
            CREATE INDEX IF NOT EXISTS idx_santri_map_santri_id 
            ON santri_map(santri_id)
        """),
        
        ("idx_santri_map_pesantren_id", """
            CREATE INDEX IF NOT EXISTS idx_santri_map_pesantren_id 
            ON santri_map(pesantren_id)
        """),
        
        ("idx_santri_skor_santri_id", """
            CREATE INDEX IF NOT EXISTS idx_santri_skor_santri_id 
            ON santri_skor(santri_id)
        """),
        
        ("idx_santri_skor_kategori", """
            CREATE INDEX IF NOT EXISTS idx_santri_skor_kategori 
            ON santri_skor(kategori_kemiskinan)
        """),
        
        ("idx_pesantren_skor_pesantren_id", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_skor_pesantren_id 
            ON pesantren_skor(pesantren_id)
        """),
        
        ("idx_pesantren_skor_kategori", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_skor_kategori 
            ON pesantren_skor(kategori_kelayakan)
        """),
        
        # Kabupaten/Provinsi filters
        ("idx_santri_pribadi_kabupaten", """
            CREATE INDEX IF NOT EXISTS idx_santri_pribadi_kabupaten 
            ON santri_pribadi(kabupaten, provinsi) 
            WHERE kabupaten IS NOT NULL
        """),
        
        ("idx_pesantren_kabupaten", """
            CREATE INDEX IF NOT EXISTS idx_pesantren_kabupaten 
            ON pondok_pesantren(kabupaten, provinsi) 
            WHERE kabupaten IS NOT NULL
        """),
    ]
    
    created = 0
    failed = 0
    
    for index_name, index_sql in indexes_sql:
        try:
            if dry_run:
                print(f"  [DRY RUN] Would create: {index_name}")
            else:
                print(f"  Creating: {index_name}...", end=" ")
                start_time = datetime.now()
                cursor.execute(index_sql)
                conn.commit()
                duration = (datetime.now() - start_time).total_seconds()
                print(f"✓ ({duration:.2f}s)")
                created += 1
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            failed += 1
            conn.rollback()
    
    cursor.close()
    
    if not dry_run:
        print(f"\n📊 Summary: {created} created, {failed} failed")
    
    return created, failed

def test_query_performance(conn):
    """Test query performance with EXPLAIN ANALYZE"""
    print("\n" + "="*80)
    print("⚡ TESTING QUERY PERFORMANCE")
    print("="*80)
    
    cursor = conn.cursor()
    
    test_queries = [
        ("Santri Map - Spatial Filter", """
            SELECT COUNT(*) 
            FROM santri_map 
            WHERE lokasi IS NOT NULL 
            LIMIT 1000
        """),
        
        ("Santri Map - Category Filter", """
            SELECT COUNT(*) 
            FROM santri_map 
            WHERE kategori_kemiskinan = 'Sangat Miskin'
        """),
        
        ("Pesantren Map - Spatial Filter", """
            SELECT COUNT(*) 
            FROM pesantren_map 
            WHERE lokasi IS NOT NULL
        """),
        
        ("Choropleth Stats Query", """
            SELECT 
                COALESCE(sp.kabupaten, 'Unknown') as kabupaten,
                COUNT(DISTINCT sp.id) as total_santri,
                COUNT(DISTINCT sp.id) FILTER (WHERE sk.kategori_kemiskinan = 'Sangat Miskin') as sangat_miskin
            FROM santri_pribadi sp
            LEFT JOIN santri_skor sk ON sp.id = sk.santri_id
            WHERE sp.kabupaten IS NOT NULL
            GROUP BY sp.kabupaten
            LIMIT 10
        """),
    ]
    
    for query_name, query in test_queries:
        print(f"\n🔍 {query_name}")
        print("-" * 80)
        try:
            cursor.execute(f"EXPLAIN ANALYZE {query}")
            explain_result = cursor.fetchall()
            
            # Print EXPLAIN output
            for row in explain_result:
                print(f"  {row[0]}")
            
            # Extract execution time
            for row in explain_result:
                if "Execution Time:" in row[0]:
                    time_str = row[0].split(":")[1].strip().split()[0]
                    print(f"\n  ⏱️  Execution Time: {time_str} ms")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    cursor.close()

def check_index_usage(conn):
    """Check if indexes are being used"""
    print("\n" + "="*80)
    print("📈 INDEX USAGE STATISTICS")
    print("="*80)
    
    cursor = conn.cursor()
    
    query = """
    SELECT 
        schemaname,
        relname,
        indexrelname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
        AND relname IN ('santri_map', 'pesantren_map', 'santri_pribadi', 
                        'pondok_pesantren', 'santri_skor', 'pesantren_skor')
    ORDER BY idx_scan DESC NULLS LAST;
    """
    
    try:
        cursor.execute(query)
        stats = cursor.fetchall()
        
        if stats:
            print(f"\n{'Table':<25} | {'Index':<35} | {'Scans':<10} | {'Tuples Read':<15}")
            print("-" * 100)
            for schema, table, index, scans, tuples_read, tuples_fetched in stats:
                print(f"{table:<25} | {index:<35} | {scans or 0:<10} | {tuples_read or 0:<15,}")
        else:
            print("⚠️  No index usage statistics found")
    except Exception as e:
        print(f"⚠️  Could not retrieve index statistics: {e}")
    
    cursor.close()

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🚀 GIS DATABASE OPTIMIZATION TEST")
    print("="*80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        print("\n📡 Connecting to database...")
        conn = get_connection()
        print("✓ Connected successfully")
        
        # Run checks
        check_table_sizes(conn)
        check_spatial_columns(conn)
        check_existing_indexes(conn)
        
        # Ask user confirmation
        print("\n" + "="*80)
        response = input("\n❓ Do you want to CREATE INDEXES? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            create_optimization_indexes(conn, dry_run=False)
            
            # After creating indexes, check again
            print("\n" + "="*80)
            print("🔄 RE-CHECKING INDEXES AFTER CREATION")
            print("="*80)
            check_existing_indexes(conn)
            
            # Test performance
            test_query_performance(conn)
            check_index_usage(conn)
        else:
            print("\n⚠️  Skipping index creation (dry run mode)")
            create_optimization_indexes(conn, dry_run=True)
        
        # Close connection
        conn.close()
        print("\n✓ Database connection closed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"✅ COMPLETED at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
