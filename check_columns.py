import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin@localhost:5433/santri_db')
cur = conn.cursor()

print("=== PROVINSI ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'provinsi' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n=== KABUPATEN ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'kabupaten' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n=== KECAMATAN ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'kecamatan' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

cur.close()
conn.close()
