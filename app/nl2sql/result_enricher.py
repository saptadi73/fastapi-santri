"""
Result Enricher untuk memperkaya query results dengan detail lengkap dari tabel relasi.
Mendeteksi ID fields dan mengambil detail tambahan dari tabel terkait.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import json


class ResultEnricher:
    """Memperkaya query results dengan data detail dari tabel relasi."""
    
    # Mapping dari ID field ke tabel source dan kolom yang ingin diambil
    ID_FIELD_MAPPINGS = {
        "santri_id": {
            "table": "santri_pribadi",
            "columns": ["nama", "nik", "jenis_kelamin", "tempat_lahir", "tanggal_lahir",
                       "status_tinggal", "provinsi", "kabupaten", "kecamatan", "desa"],
            "join_column": "id"
        },
        "pesantren_id": {
            "table": "pondok_pesantren",
            "columns": ["nama", "alamat", "desa", "kecamatan", "kabupaten", "provinsi", 
                       "kontak_telepon", "email", "website", "nama_kyai", "jumlah_santri", 
                       "jumlah_guru", "tahun_berdiri"],
            "join_column": "id"
        },
        "id": {
            # Default untuk ID - coba deteksi dari query context
            "columns": ["nama", "nama_santri", "nama_pesantren", "title", "description"],
            "auto_detect": True
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def enrich(self, results: List[Dict[str, Any]], sql_query: str) -> List[Dict[str, Any]]:
        """
        Perkaya hasil query dengan detail tambahan dari tabel relasi.
        
        Args:
            results: List of query results (dictionaries)
            sql_query: Original SQL query (untuk context)
            
        Returns:
            List of enriched results dengan detail tambahan
        """
        if not results or len(results) == 0:
            return results
        
        try:
            # Dapatkan list field yang ada di result
            first_row = results[0]
            result_fields = set(first_row.keys())
            
            # Cek apakah ada ID field yang bisa di-enrich
            for id_field in self.ID_FIELD_MAPPINGS.keys():
                if id_field in result_fields:
                    results = self._enrich_with_field(
                        results, 
                        id_field, 
                        self.ID_FIELD_MAPPINGS[id_field],
                        sql_query
                    )
            
            return results
            
        except Exception as e:
            print(f"Warning: Error enriching results: {str(e)}")
            return results
    
    def _enrich_with_field(
        self, 
        results: List[Dict[str, Any]], 
        id_field: str, 
        mapping: Dict[str, Any],
        sql_query: str
    ) -> List[Dict[str, Any]]:
        """
        Enrich results untuk specific ID field.
        
        Args:
            results: List of results
            id_field: Field name (e.g., 'santri_id')
            mapping: Mapping configuration untuk field ini
            sql_query: Original SQL query
            
        Returns:
            Enriched results
        """
        try:
            if mapping.get("auto_detect"):
                # Skip auto-detect untuk ID field generic
                return results
            
            table_name = mapping.get("table")
            columns = mapping.get("columns", [])
            join_column = mapping.get("join_column", "id")
            
            if not table_name or not columns:
                return results
            
            # Extract unique IDs dari results
            ids = list(set(
                row.get(id_field) 
                for row in results 
                if row.get(id_field) is not None
            ))
            
            if not ids:
                return results
            
            # Build query untuk ambil detail
            # Escape IDs yang string
            id_placeholders = ", ".join([
                f"'{str(id_).replace(chr(39), chr(39)+chr(39))}'" 
                if isinstance(id_, str) else str(id_)
                for id_ in ids[:100]  # Limit 100 IDs per query
            ])
            
            try:
                # Filter columns yang actually exist (try safe approach)
                # Fetch data with selected columns
                detail_query = f"""
                    SELECT {join_column}, {', '.join(columns)}
                    FROM {table_name}
                    WHERE {join_column} IN ({id_placeholders})
                    LIMIT 1000
                """
                
                print(f"[DEBUG] Enriching {id_field} from {table_name}")
                print(f"[DEBUG] IDs to fetch: {len(ids)}")
                
                detail_query = f"""
                    SELECT {join_column}, {', '.join(columns)}
                    FROM {table_name}
                    WHERE {join_column} IN ({id_placeholders})
                    LIMIT 1000
                """
                
                detail_results = self.db.execute(text(detail_query)).fetchall()
                print(f"[DEBUG] Fetched {len(detail_results)} detail rows")
                
                # Convert to dict for easier lookup
                details_map = {}
                for row in detail_results:
                    row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
                    # Store with both UUID and string representations as keys
                    id_value = row_dict[join_column]
                    details_map[id_value] = row_dict
                    # Also store as string version jika UUID
                    if hasattr(id_value, '__str__'):
                        details_map[str(id_value)] = row_dict
                
                # Merge detail ke dalam results
                enriched_results = []
                for row in results:
                    enriched_row = dict(row)
                    id_value = row.get(id_field)
                    
                    if id_value in details_map:
                        detail = details_map[id_value]
                        # Tambah kolom detail, hindari duplikasi
                        for col, value in detail.items():
                            if col != join_column and col not in enriched_row:
                                enriched_row[col] = value
                    
                    enriched_results.append(enriched_row)
                
                return enriched_results
                
            except Exception as e:
                print(f"Warning: Could not fetch details from {table_name}: {str(e)}")
                return results
        
        except Exception as e:
            print(f"Warning: Error in _enrich_with_field: {str(e)}")
            return results
    
    @staticmethod
    def get_detail_fields_for_query(sql_query: str) -> Dict[str, List[str]]:
        """
        Analisis SQL query untuk mendeteksi intent dan suggested detail fields.
        
        Args:
            sql_query: SQL query string
            
        Returns:
            Dictionary berisi suggested enrichment fields
        """
        suggested_details = {}
        
        query_upper = sql_query.upper()
        
        # Deteksi tabel yang di-query
        if "SANTRI_PRIBADI" in query_upper:
            suggested_details["santri_details"] = [
                "nama_santri", "nomer_induk", "alamat", "jenis_kelamin", 
                "kategori_kemiskinan", "tanggal_lahir"
            ]
        
        if "PONDOK_PESANTREN" in query_upper:
            suggested_details["pesantren_details"] = [
                "nama", "alamat", "kabupaten", "provinsi", "kontak_telepon", "nama_kyai"
            ]
        
        return suggested_details
