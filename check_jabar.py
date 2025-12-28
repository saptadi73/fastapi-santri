import psycopg2

conn = psycopg2.connect('postgresql://postgres:admin@localhost:5433/santri_db')
cur = conn.cursor()

print("=== Kabupaten di Jawa Barat ===")
cur.execute("SELECT DISTINCT name_2 FROM kabupaten WHERE name_1 = 'JawaBarat' ORDER BY name_2 LIMIT 15")
for row in cur.fetchall():
    if row[0]:
        print(row[0])

cur.close()
conn.close()
