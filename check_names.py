import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin@localhost:5433/santri_db')
cur = conn.cursor()

print("=== Nama Provinsi yang tersedia ===")
cur.execute("SELECT DISTINCT name_1 FROM provinsi ORDER BY name_1")
for row in cur.fetchall():
    if row[0]:
        print(row[0])

print("\n=== Sample Kabupaten ===")
cur.execute("SELECT DISTINCT name_2 FROM kabupaten ORDER BY name_2 LIMIT 10")
for row in cur.fetchall():
    if row[0]:
        print(row[0])

cur.close()
conn.close()
