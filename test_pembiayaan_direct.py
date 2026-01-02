"""Direct SQL test to verify pembiayaan scoring fix."""

import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

# Extract connection info from DATABASE_URL
# Format: postgresql://user:password@host:port/database
db_url = settings.database_url
db_url = db_url.replace("postgresql://", "")
user_pass, host_db = db_url.split("@")
user, password = user_pass.split(":")
host_port, database = host_db.split("/")
host, port = host_port.split(":")

# Connect to database
conn = psycopg2.connect(
    host=host,
    port=port,
    database=database,
    user=user,
    password=password
)

santri_id = '1eee8ac2-2d33-4795-8691-ca5f165d2972'
pembiayaan_id = '5beff917-8555-475c-b93b-605aff977470'

print("=" * 60)
print("Direct Database Query - Pembiayaan Data")
print("=" * 60)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    # Get pembiayaan data
    cur.execute("""
        SELECT 
            id, santri_id, sumber_biaya, status_pembayaran, 
            tunggakan_bulan, biaya_per_bulan
        FROM santri_pembiayaan 
        WHERE santri_id = %s
    """, (santri_id,))
    
    pembiayaan = cur.fetchone()
    
    if pembiayaan:
        print("\nPembiayaan Record:")
        print(f"  ID: {pembiayaan['id']}")
        print(f"  Santri ID: {pembiayaan['santri_id']}")
        print(f"  Sumber Biaya: {pembiayaan['sumber_biaya']}")
        print(f"  Status Pembayaran: {pembiayaan['status_pembayaran']}")
        print(f"  Tunggakan Bulan: {pembiayaan['tunggakan_bulan']}")
        print(f"  Biaya Per Bulan: {pembiayaan['biaya_per_bulan']}")
        
        print("\n" + "=" * 60)
        print("Expected Scoring Calculation:")
        print("=" * 60)
        
        # Calculate expected scores based on scoring.json rules
        sumber_biaya_scores = {
            "donatur": 10,
            "beasiswa": 8,
            "wali": 5,
            "orang_tua": 2
        }
        
        status_pembayaran_scores = {
            "menunggak": 10,
            "terlambat": 5,
            "lancar": 0
        }
        
        sumber_score = sumber_biaya_scores.get(pembiayaan['sumber_biaya'], 0)
        status_score = status_pembayaran_scores.get(pembiayaan['status_pembayaran'], 3)  # 3 is is_null default
        
        tunggakan_score = 0
        tunggakan = pembiayaan['tunggakan_bulan']
        if tunggakan is None:
            tunggakan_score = 2  # is_null score
        elif tunggakan >= 3:
            tunggakan_score = 5
        elif tunggakan >= 1:
            tunggakan_score = 3
        elif tunggakan == 0:
            tunggakan_score = 0
        
        print(f"\nSumber Biaya '{pembiayaan['sumber_biaya']}' -> Score: {sumber_score}")
        print(f"Status Pembayaran '{pembiayaan['status_pembayaran']}' -> Score: {status_score}")
        print(f"Tunggakan Bulan {pembiayaan['tunggakan_bulan']} -> Score: {tunggakan_score}")
        print(f"\nTotal Pembiayaan Score: {sumber_score + status_score + tunggakan_score}/25")
        
        # Get scoring record if exists
        cur.execute("""
            SELECT 
                skor_pembiayaan, skor_total, kategori_kemiskinan,
                created_at, updated_at
            FROM santri_skor 
            WHERE santri_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (santri_id,))
        
        skor = cur.fetchone()
        
        if skor:
            print("\n" + "=" * 60)
            print("Current Scoring Record (Before Fix):")
            print("=" * 60)
            print(f"  Pembiayaan Score: {skor['skor_pembiayaan']}")
            print(f"  Total Score: {skor['skor_total']}")
            print(f"  Kategori: {skor['kategori_kemiskinan']}")
            print(f"  Last Updated: {skor['updated_at']}")
            print("\nNote: This may show old values if scoring hasn't been recalculated yet.")
        else:
            print("\nNo scoring record found yet for this santri.")
    else:
        print(f"\nNo pembiayaan record found for santri {santri_id}")

conn.close()

print("\n" + "=" * 60)
print("Fix Applied:")
print("=" * 60)
print("✓ Added status_pembayaran mapping in get_param_value()")
print("✓ Added tunggakan_bulan mapping in get_param_value()")
print("✓ Added is_null operator support for NULL handling")
print("✓ Added empty/not_empty operators for string field checks")
print("✓ Added status_gizi, riwayat_penyakit, kebutuhan_khusus mappings")
print("\nTo apply the fix, recalculate scoring using:")
print(f"POST /api/scoring/{santri_id}/calculate")
print("=" * 60)
