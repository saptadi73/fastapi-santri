"""
Generate NL2SQL schema context directly from current database
This ensures NL2SQL uses the most up-to-date schema
"""
import json
from app.core.database import engine
from sqlalchemy import text, inspect

def generate_schema_context():
    """Generate comprehensive schema context from database"""
    
    inspector = inspect(engine)
    schema_context = {
        "database": "PostgreSQL + PostGIS",
        "generated_from": "Database schema extraction",
        "last_updated": "2025-01-15",
        "rules": [
            "Gunakan hanya SELECT (tidak boleh UPDATE/INSERT/DELETE)",
            "Selalu gunakan LIMIT <= 1000",
            "Gunakan ST_DWithin untuk query radius (meter)",
            "Gunakan ST_Intersects untuk query polygon/area",
            "Untuk geometry: gunakan ST_Distance, ST_Within, ST_Contains",
            "Jangan gunakan tabel di luar schema ini",
            "Format tanggal: YYYY-MM-DD"
        ],
        "tables": {}
    }
    
    # Tables to document for NL2SQL
    important_tables = [
        'pondok_pesantren',
        'pesantren_map',
        'pesantren_fisik',
        'pesantren_fasilitas',
        'pesantren_pendidikan',
        'pesantren_skor',
        'santri',
        'santri_pribadi',
        'santri_map',
        'santri_orangtua',
        'santri_rumah',
        'santri_kesehatan',
        'santri_pembiayaan',
        'santri_bansos',
        'santri_asset',
        'santri_skor'
    ]
    
    table_descriptions = {
        'pondok_pesantren': 'Data utama pondok pesantren',
        'pesantren_map': 'Data spasial lokasi pesantren untuk GIS mapping dengan lokasi geometri',
        'pesantren_fisik': 'Data kondisi fisik dan infrastruktur pesantren',
        'pesantren_fasilitas': 'Fasilitas dan layanan yang dimiliki pesantren',
        'pesantren_pendidikan': 'Jenjang pendidikan yang diselenggarakan pesantren',
        'pesantren_skor': 'Hasil penilaian kelayakan pesantren (scoring)',
        'santri': 'Relasi santri dengan pesantren',
        'santri_pribadi': 'Data pribadi santri dengan informasi lokasi',
        'santri_map': 'Lokasi tempat tinggal santri untuk GIS mapping dengan geometri',
        'santri_orangtua': 'Data orang tua/wali santri untuk penilaian ekonomi',
        'santri_rumah': 'Data kondisi rumah/tempat tinggal santri',
        'santri_kesehatan': 'Data kondisi kesehatan dan gizi santri',
        'santri_pembiayaan': 'Data biaya dan sumber pembiayaan pendidikan santri',
        'santri_bansos': 'Program bantuan sosial yang diterima santri',
        'santri_asset': 'Aset/barang berharga yang dimiliki keluarga santri',
        'santri_skor': 'Hasil scoring tingkat kemiskinan santri (aggregate score)',
    }
    
    # Get columns for each table
    with engine.connect() as conn:
        for table_name in important_tables:
            if table_name not in inspector.get_table_names():
                continue
                
            columns = inspector.get_columns(table_name)
            
            # Get primary and foreign keys
            pk = inspector.get_pk_constraint(table_name)
            fks = inspector.get_foreign_keys(table_name)
            
            schema_context["tables"][table_name] = {
                "description": table_descriptions.get(table_name, ""),
                "columns": {}
            }
            
            # Get column constraints for better descriptions
            constraints_info = {}
            try:
                result = conn.execute(text(f"""
                    SELECT constraint_name, constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_name = '{table_name}'
                """))
                for row in result:
                    constraints_info[row[0]] = row[1]
            except:
                pass
            
            # Build column info
            for col in columns:
                col_name = col['name']
                col_type = str(col['type'])
                is_pk = pk and col_name in pk.get('constrained_columns', [])
                is_fk = any(col_name in fk['constrained_columns'] for fk in fks)
                nullable = col['nullable']
                
                # Build description
                desc_parts = []
                
                if is_pk:
                    desc_parts.append("UUID primary key")
                
                # Check for foreign keys
                for fk in fks:
                    if col_name in fk['constrained_columns']:
                        ref_table = fk['referred_table']
                        ref_col = fk['referred_columns'][0] if fk['referred_columns'] else 'id'
                        desc_parts.append(f"UUID FK ke {ref_table}.{ref_col}")
                
                if not desc_parts:
                    # Generic type description
                    if 'VARCHAR' in col_type or 'CHAR' in col_type:
                        desc_parts.append("String")
                    elif 'INT' in col_type:
                        desc_parts.append("Integer")
                    elif 'DOUBLE' in col_type or 'FLOAT' in col_type:
                        desc_parts.append("Float")
                    elif 'BOOLEAN' in col_type:
                        desc_parts.append("Boolean")
                    elif 'DATE' in col_type:
                        desc_parts.append("Date (YYYY-MM-DD)")
                    elif 'TIMESTAMP' in col_type:
                        desc_parts.append("Timestamp")
                    elif 'geometry' in col_type:
                        desc_parts.append("Geometry POINT (SRID 4326) - koordinat lat/lon")
                    else:
                        desc_parts.append(col_type)
                
                if not nullable and not is_pk:
                    desc_parts.append("NOT NULL")
                
                schema_context["tables"][table_name]["columns"][col_name] = " - ".join(desc_parts)
    
    return schema_context


def main():
    try:
        print("=" * 80)
        print("GENERATING NL2SQL SCHEMA CONTEXT FROM DATABASE")
        print("=" * 80)
        
        schema = generate_schema_context()
        
        # Save to file
        schema_file = 'app/nl2sql/schema_context.json'
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"\n✅ Schema context generated and saved to: {schema_file}")
        print(f"\nTables included: {len(schema['tables'])}")
        for table_name in schema['tables']:
            col_count = len(schema['tables'][table_name]['columns'])
            print(f"  - {table_name}: {col_count} columns")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
