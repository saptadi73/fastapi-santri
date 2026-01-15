"""NL2SQL Service with Intent Detection and Query Execution."""

import json
import os
import re
from typing import Optional, Any
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.nl2sql.intent_classifier import IntentClassifier, IntentType, IntentResponse
from app.nl2sql.result_enricher import ResultEnricher


def load_schema_context() -> dict:
    """Load schema context from JSON file."""
    schema_file = os.path.join(
        os.path.dirname(__file__),
        "schema_context.json"
    )
    
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Schema context file not found: {schema_file}")
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


class NL2SQLService:
    """Service untuk convert natural language ke SQL dengan intent detection."""
    
    def __init__(self, db: Session):
        self.db = db
        self.classifier = IntentClassifier()
        self.schema = load_schema_context()
        try:
            self.enricher = ResultEnricher(db)
            print("[NL2SQL] ResultEnricher initialized successfully")
        except Exception as e:
            print(f"[NL2SQL] Error initializing enricher: {str(e)}")
            self.enricher = None
    
    def process_query(self, user_query: str) -> dict[str, Any]:
        """
        Process natural language query end-to-end.
        
        Args:
            user_query: User's natural language input
            
        Returns:
            {
                "intent": IntentResponse,
                "sql_query": str,
                "result": list | dict,
                "execution_time_ms": float,
                "error": str (if any)
            }
        """
        try:
            # 1. Classify intent
            intent_response = self.classifier.classify(user_query)
            
            # 2. Generate SQL based on intent
            sql_query = self.generate_sql(user_query, intent_response)
            print(f"[NL2SQL] Generated SQL (raw): {sql_query[:200]}")
            
            # 3. Validate SQL
            validation = self.validate_sql(sql_query)
            if not validation["is_valid"]:
                return {
                    "intent": intent_response,
                    "sql_query": sql_query,
                    "error": validation["error"],
                    "result": None
                }
            
            # 4. Execute SQL
            start_time = datetime.now()
            result = self.execute_sql(sql_query)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 5. Enrich results dengan detail dari tabel relasi
            print(f"[NL2SQL] Before enrichment: result type={type(result)}, length={len(result) if isinstance(result, list) else 'N/A'}")
            if isinstance(result, list) and len(result) > 0:
                print(f"[NL2SQL] First row before enrichment: {list(result[0].keys()) if isinstance(result[0], dict) else 'N/A'}")
                if self.enricher:
                    try:
                        result = self.enricher.enrich(result, sql_query)
                        print(f"[NL2SQL] First row after enrichment: {list(result[0].keys()) if isinstance(result[0], dict) else 'N/A'}")
                    except Exception as e:
                        print(f"[NL2SQL] Error during enrichment: {str(e)}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("[NL2SQL] Enricher is None, skipping enrichment")
            
            return {
                "intent": intent_response,
                "sql_query": sql_query,
                "result": result,
                "execution_time_ms": execution_time,
                "error": None
            }
            
        except Exception as e:
            return {
                "intent": None,
                "sql_query": None,
                "result": None,
                "error": str(e)
            }
    
    def generate_sql(self, user_query: str, intent: IntentResponse) -> str:
        """
        Generate SQL query using OpenAI.
        
        Args:
            user_query: Natural language query
            intent: Detected intent
            
        Returns:
            SQL query string
        """
        schema_str = json.dumps(self.schema, indent=2)
        
        system_prompt = """Anda adalah ahli SQL untuk PostgreSQL + PostGIS. 
Ubah pertanyaan dalam bahasa natural menjadi SQL query HANYA SELECT yang aman.

ATURAN KETAT:
1. Hanya SELECT queries (tidak boleh UPDATE/INSERT/DELETE)
2. Selalu gunakan LIMIT <= 1000
3. **WAJIB MEMBACA query_examples dari schema - IKUTI POLA TERSEBUT**
4. **PENTING: Gunakan JOIN untuk mendapatkan detail lengkap (nama, alamat, dll)**
   - Untuk santri dengan score: JOIN santri_skor dengan santri_pribadi ON santri_skor.santri_id = santri_pribadi.id
   - Untuk pesantren dengan score: JOIN pesantren_skor dengan pondok_pesantren ON pesantren_skor.pesantren_id = pondok_pesantren.id
   - JANGAN hanya SELECT ID saja, SELECT juga nama, alamat, dan kolom detail lainnya
5. **SANGAT PENTING - KOORDINAT UNTUK PETA (WAJIB!):**
   - Jika query tentang SANTRI dan tidak ada GROUP BY: SELALU SELECT latitude, longitude dari santri_pribadi
     Contoh: SELECT sp.id, sp.nama, sp.latitude, sp.longitude, ss.skor_total FROM santri_pribadi sp JOIN santri_skor ss ON sp.id = ss.santri_id ...
   - Jika query tentang PESANTREN dan tidak ada GROUP BY: JOIN dengan pesantren_map dan WAJIB extract koordinat menggunakan ST_X() dan ST_Y()
     Contoh: SELECT pp.id, pp.nama, ps.skor_total, ST_Y(pm.lokasi::geometry) as latitude, ST_X(pm.lokasi::geometry) as longitude FROM pondok_pesantren pp JOIN pesantren_skor ps ON pp.id = ps.pesantren_id JOIN pesantren_map pm ON pp.id = pm.pesantren_id ...
   - TANPA KOORDINAT = QUERY SALAH
6. **Untuk agregasi per wilayah (kabupaten/provinsi):**
   - Gunakan GROUP BY kabupaten/provinsi
   - Gunakan aggregate functions: COUNT(*), AVG(skor_total), SUM(), MAX(), MIN()
   - Jangan include latitude/longitude pada agregasi
7. **PENTING: Gunakan enum values yang TEPAT (case-sensitive):**
   - kualitas_air_bersih: 'layak_minum', 'berbau', 'keruh', 'asin' (lowercase dengan underscore)
   - fasilitas_mck: 'lengkap', 'kurang_lengkap', 'tidak_layak' (lowercase dengan underscore)
   - kategori_kemiskinan: 'Tidak Miskin', 'Rentan Miskin', 'Miskin', 'Sangat Miskin' (dengan spasi dan kapital)
8. LIHAT query_examples di schema untuk exact pattern - ikuti yang paling sesuai
9. Untuk geometry: gunakan ST_Distance, ST_Within, ST_Contains, ST_Intersects
10. Jangan gunakan tabel di luar schema yang diberikan

Output HANYA SQL query tanpa penjelasan lainnya.
Jika query terlalu ambigu, buat query yang paling masuk akal berdasarkan context.

SCHEMA DATABASE:
""" + schema_str
        
        user_prompt = f"""Intent terdeteksi: {intent.intent.value}
Entities: {', '.join(intent.entity_types)}

User query: {user_query}

Buat SQL SELECT query yang aman dan efisien.
Jika query meminta aggregasi per wilayah (kabupaten/provinsi), gunakan GROUP BY dengan aggregate functions (COUNT, AVG, SUM).

INSTRUKSI SPESIAL:
- Jika query memiliki entity "pesantren" dan BUKAN agregasi: WAJIB JOIN dengan pesantren_map dan extract koordinat dengan ST_Y(pm.lokasi::geometry) as latitude, ST_X(pm.lokasi::geometry) as longitude
- Jika query memiliki entity "santri" dan BUKAN agregasi: WAJIB SELECT latitude, longitude dari santri_pribadi

Jika tidak bisa dipahami, buat query yang paling reasonable berdasarkan intent."""
        
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                max_tokens=settings.nl2sql_max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")
            
            sql = content.strip()
            
            # Clean SQL (remove markdown code blocks if any)
            sql = re.sub(r'^```sql\n', '', sql)
            sql = re.sub(r'\n```$', '', sql)
            sql = sql.strip()
            
            return sql
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def validate_sql(self, sql_query: str) -> dict[str, Any]:
        """
        Validate SQL query for safety.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            {"is_valid": bool, "error": str}
        """
        # Check for dangerous keywords
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]
        sql_upper = sql_query.upper().strip()
        
        for keyword in dangerous_keywords:
            if sql_upper.startswith(keyword):
                return {
                    "is_valid": False,
                    "error": f"Query tidak boleh menggunakan {keyword}"
                }
        
        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return {
                "is_valid": False,
                "error": "Query harus berupa SELECT statement"
            }
        
        # Check LIMIT
        if "LIMIT" not in sql_upper:
            return {
                "is_valid": False,
                "error": "Query harus memiliki LIMIT clause"
            }
        
        # Check if LIMIT value <= 1000
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > 1000:
                return {
                    "is_valid": False,
                    "error": f"LIMIT tidak boleh lebih dari 1000 (current: {limit_value})"
                }
        
        return {"is_valid": True, "error": None}
    
    def execute_sql(self, sql_query: str) -> list[dict]:
        """
        Execute SQL query safely.
        
        Args:
            sql_query: Validated SQL query
            
        Returns:
            List of result rows as dicts
        """
        try:
            result = self.db.execute(text(sql_query))
            
            # Convert to list of dicts
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            
            return rows
            
        except Exception as e:
            raise Exception(f"Database execution error: {str(e)}")
