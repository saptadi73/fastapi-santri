"""
Check all enum fields for invalid values that don't match the defined enums
"""
from app.core.database import engine
from sqlalchemy import text

# Define all enum fields and their valid values
ENUM_FIELDS = {
    "santri_pribadi": {
        "jenis_kelamin": ["L", "P"],
        "status_tinggal": ["mondok", "pp", "mukim"],
    },
    "santri_rumah": {
        "status_rumah": ["milik_sendiri", "kontrak", "menumpang"],
        "jenis_lantai": ["tanah", "semen", "keramik"],
        "jenis_dinding": ["bambu", "kayu", "tembok"],
        "jenis_atap": ["rumbia", "seng", "genteng", "beton"],
        "akses_air": ["layak", "tidak_layak"],
    },
    "santri_pembiayaan": {
        "sumber_biaya": ["orang_tua", "wali", "donatur", "beasiswa"],
        "status_pembayaran": ["lancar", "terlambat", "menunggak"],
    },
    "santri_orangtua": {
        "hubungan": ["ayah", "ibu", "wali"],
        "status_hidup": ["hidup", "meninggal"],
    },
    "santri_kesehatan": {
        "status_gizi": ["baik", "kurang", "lebih"],
    },
}

def check_all_enums():
    """Check all enum fields for invalid values"""
    with engine.connect() as connection:
        issues_found = []
        
        for table_name, fields in ENUM_FIELDS.items():
            for field_name, valid_values in fields.items():
                try:
                    # Get distinct values
                    result = connection.execute(
                        text(f"SELECT DISTINCT {field_name} FROM {table_name} WHERE {field_name} IS NOT NULL")
                    )
                    current_values = [row[0] for row in result]
                    
                    # Check for invalid values
                    invalid_values = [v for v in current_values if v not in valid_values]
                    
                    if invalid_values:
                        placeholders = ','.join([f"'{v}'" for v in invalid_values])
                        count = connection.execute(
                            text(f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} IN ({placeholders})")
                        ).scalar()
                        issues_found.append({
                            "table": table_name,
                            "field": field_name,
                            "invalid_values": invalid_values,
                            "count": count,
                            "valid_values": valid_values,
                        })
                        print(f"✗ {table_name}.{field_name}: Found {count} invalid values: {invalid_values}")
                    else:
                        print(f"✓ {table_name}.{field_name}: All values valid {current_values}")
                        
                except Exception as e:
                    print(f"✗ Error checking {table_name}.{field_name}: {e}")
        
        return issues_found

if __name__ == "__main__":
    print("Checking all enum fields...\n")
    issues = check_all_enums()
    print(f"\nTotal issues found: {len(issues)}")
    if issues:
        print("\nSummary:")
        for issue in issues:
            print(f"  {issue['table']}.{issue['field']}: {issue['count']} invalid records with values {issue['invalid_values']}")
