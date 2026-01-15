"""
Complete verification of all enum fixes
"""
from app.core.database import engine
from sqlalchemy import text

def verify_all_enums():
    """Verify all enum values are now correct"""
    with engine.connect() as conn:
        all_enums = {
            'santri_pribadi': {
                'jenis_kelamin': ['L', 'P'],
                'status_tinggal': ['mondok', 'pp', 'mukim'],
            },
            'santri_rumah': {
                'status_rumah': ['milik_sendiri', 'kontrak', 'menumpang'],
                'jenis_lantai': ['tanah', 'semen', 'keramik'],
                'jenis_dinding': ['bambu', 'kayu', 'tembok'],
                'jenis_atap': ['rumbia', 'seng', 'genteng', 'beton'],
                'akses_air_bersih': ['layak', 'tidak_layak'],
            },
            'santri_pembiayaan': {
                'sumber_biaya': ['orang_tua', 'wali', 'donatur', 'beasiswa'],
                'status_pembayaran': ['lancar', 'terlambat', 'menunggak'],
            },
            'santri_orangtua': {
                'hubungan': ['ayah', 'ibu', 'wali'],
                'status_hidup': ['hidup', 'meninggal'],
            },
            'santri_kesehatan': {
                'status_gizi': ['baik', 'kurang', 'lebih'],
            },
        }
        
        print("=" * 70)
        print("ENUM VERIFICATION REPORT")
        print("=" * 70)
        
        total_tables = 0
        total_fields = 0
        all_valid = True
        
        for table, fields in all_enums.items():
            total_tables += 1
            table_valid = True
            
            for field, valid_values in fields.items():
                total_fields += 1
                try:
                    result = conn.execute(text(f'SELECT DISTINCT {field} FROM {table} WHERE {field} IS NOT NULL ORDER BY {field}'))
                    current = [r[0] for r in result]
                    invalid = [v for v in current if v not in valid_values]
                    
                    if invalid:
                        print(f"\n✗ {table}.{field}")
                        print(f"  Valid values: {valid_values}")
                        print(f"  Current values: {current}")
                        print(f"  Invalid: {invalid}")
                        all_valid = False
                        table_valid = False
                    else:
                        print(f"✓ {table}.{field}")
                        print(f"  Values: {current}")
                except Exception as e:
                    print(f"✗ {table}.{field} - Error: {str(e)[:60]}")
                    all_valid = False
                    table_valid = False
        
        print("\n" + "=" * 70)
        print(f"Summary: {total_tables} tables, {total_fields} enum fields checked")
        if all_valid:
            print("✓ ALL ENUM VALUES ARE VALID!")
        else:
            print("✗ Some invalid values still exist")
        print("=" * 70)
        
        return all_valid

if __name__ == "__main__":
    verify_all_enums()
