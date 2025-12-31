"""Check santri data for debugging scoring."""
from app.core.database import engine
import sqlalchemy as sa

santri_id = 'ae739ebe-2f19-43e1-9244-580bfb8a9acf'

with engine.connect() as conn:
    print("=== ORANGTUA (Ekonomi) ===")
    result = conn.execute(sa.text("""
        SELECT pendapatan_bulanan, pekerjaan, pendidikan_terakhir 
        FROM santri_orangtua 
        WHERE santri_id = :id
    """), {'id': santri_id})
    row = result.fetchone()
    if row:
        print(f"  Pendapatan Bulanan: {row[0]}")
        print(f"  Pekerjaan: {row[1]}")
        print(f"  Pendidikan: {row[2]}")
    else:
        print("  NOT FOUND")

    print("\n=== RUMAH ===")
    result = conn.execute(sa.text("""
        SELECT status_rumah, jenis_lantai, jenis_dinding, jenis_atap, 
               akses_air_bersih, daya_listrik_va
        FROM santri_rumah 
        WHERE santri_id = :id
    """), {'id': santri_id})
    row = result.fetchone()
    if row:
        print(f"  Status: {row[0]}")
        print(f"  Lantai: {row[1]}")
        print(f"  Dinding: {row[2]}")
        print(f"  Atap: {row[3]}")
        print(f"  Air Bersih: {row[4]}")
        print(f"  Listrik VA: {row[5]}")
    else:
        print("  NOT FOUND")

    print("\n=== PEMBIAYAAN ===")
    result = conn.execute(sa.text("""
        SELECT status_pembayaran, tunggakan_bulan, biaya_per_bulan
        FROM santri_pembiayaan 
        WHERE santri_id = :id
    """), {'id': santri_id})
    row = result.fetchone()
    if row:
        print(f"  Status: {row[0]}")
        print(f"  Tunggakan: {row[1]} bulan")
        print(f"  Biaya/bulan: Rp {row[2]:,}" if row[2] else "  Biaya/bulan: None")
    else:
        print("  NOT FOUND")

    print("\n=== KESEHATAN ===")
    result = conn.execute(sa.text("""
        SELECT status_gizi, riwayat_penyakit
        FROM santri_kesehatan 
        WHERE santri_id = :id
    """), {'id': santri_id})
    row = result.fetchone()
    if row:
        print(f"  Status Gizi: {row[0]}")
        print(f"  Riwayat Penyakit: {row[1]}")
    else:
        print("  NOT FOUND")

    print("\n=== BANSOS ===")
    result = conn.execute(sa.text("""
        SELECT pkh, bpnt, pip, kis_pbi, blt_desa
        FROM santri_bansos 
        WHERE santri_id = :id
    """), {'id': santri_id})
    row = result.fetchone()
    if row:
        print(f"  PKH: {row[0]}")
        print(f"  BPNT: {row[1]}")
        print(f"  PIP: {row[2]}")
        print(f"  KIS/PBI: {row[3]}")
        print(f"  BLT Desa: {row[4]}")
    else:
        print("  NOT FOUND")

    print("\n=== ASET ===")
    result = conn.execute(sa.text("""
        SELECT jenis_aset, jumlah, nilai_perkiraan
        FROM santri_asset 
        WHERE santri_id = :id
    """), {'id': santri_id})
    rows = result.fetchall()
    if rows:
        for i, row in enumerate(rows, 1):
            print(f"  Asset {i}: {row[0]} x{row[1]} = Rp {row[2]:,}" if row[2] else f"  Asset {i}: {row[0]} x{row[1]} = None")
    else:
        print("  NO ASSETS")
