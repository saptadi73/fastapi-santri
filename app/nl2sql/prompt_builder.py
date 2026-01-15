"""Prompt Builder untuk NL2SQL - Bangun prompt yang optimal untuk OpenAI."""

from typing import Dict, Any, List, Optional
from app.nl2sql.intent_classifier import IntentResponse


class PromptBuilder:
    """Build optimized prompts untuk OpenAI API."""
    
    @staticmethod
    def build_system_prompt(schema: Dict[str, Any], additional_context: str = "") -> str:
        """
        Build system prompt untuk SQL generation.
        
        Args:
            schema: Database schema context
            additional_context: Additional context/rules
            
        Returns:
            System prompt string
        """
        schema_str = PromptBuilder._format_schema(schema)
        
        system_prompt = f"""Anda adalah expert SQL database engineer. 
Tugas Anda adalah menghasilkan SQL SELECT queries yang aman dan efisien.

RULES:
- HANYA gunakan SELECT queries (tidak boleh DROP, DELETE, UPDATE, INSERT)
- WAJIB tambahkan LIMIT clause (maksimal 1000)
- Query harus aman dari SQL injection
- Gunakan table aliases untuk clarity
- Gunakan proper JOINs jika perlu multiple tables
- Filter harus menggunakan proper WHERE clauses
- Untuk geografis queries, gunakan ST_DWithin, ST_Intersects, ST_X, ST_Y
- Format tanggal: YYYY-MM-DD
- Jika tidak yakin field/table, gunakan yang paling mirip
- Jika tidak bisa membuat query yang aman/benar, response dengan: "ERROR: Deskripsi masalah"

SCHEMA DATABASE:
{schema_str}

{additional_context}

Format response: HANYA SQL query tanpa penjelasan tambahan."""
        
        return system_prompt
    
    @staticmethod
    def build_user_prompt(
        query: str,
        intent: IntentResponse,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Build user prompt dengan context dari intent detection.
        
        Args:
            query: User's natural language query
            intent: IntentResponse dari classifier
            history: Previous conversation history (optional)
            
        Returns:
            User prompt string
        """
        prompt = f"""Intent: {intent.intent.value}
Confidence: {intent.confidence:.2%}
Entities: {', '.join(intent.entity_types) if intent.entity_types else 'None'}
Description: {intent.description}

User Query: {query}

Generate SQL:"""
        
        if history:
            prompt = "CONVERSATION HISTORY:\n"
            for msg in history:
                prompt += f"- {msg.get('role', 'user')}: {msg.get('content', '')}\n"
            prompt += f"\nCurrent Query: {query}\n\nGenerate SQL:"
        
        return prompt
    
    @staticmethod
    def build_list_intent_prompt(query: str, entity: str, limit: int = 100) -> str:
        """Build optimized prompt untuk LIST intent."""
        return f"""Intent: LIST
Query: {query}
Entity: {entity}

Generate SELECT query untuk mengambil {limit} records dari {entity} table.
Include semua relevant fields.
Gunakan hanya kolom yang ada di schema_context.json.
Jika butuh urutan terbaru: gunakan created_at DESC bila kolom tersebut ada;
jika tidak ada created_at maka gunakan updated_at DESC; jika keduanya tidak ada,
gunakan id DESC sebagai fallback aman.

Jika query memunculkan id saja, tambahkan kolom yang bermakna manusia (nama/alamat/deskripsi)
melalui JOIN ke tabel induk yang sesuai. Contoh:
- pesantren_skor -> join pondok_pesantren untuk nama, alamat, kabupaten, provinsi
- santri -> join santri_pribadi untuk nama dan lokasi/demografi
Jaga LIMIT <= 1000.

Generate SQL:"""
    
    @staticmethod
    def build_filter_intent_prompt(
        query: str,
        entities: List[str],
        conditions: Optional[List[str]] = None
    ) -> str:
        """Build optimized prompt untuk FILTER intent."""
        conditions_str = ""
        if conditions:
            conditions_str = f"\nDetected conditions:\n" + "\n".join(f"- {c}" for c in conditions)
        
        return f"""Intent: FILTER
Query: {query}
Entities: {', '.join(entities)}
{conditions_str}

Generate SELECT query dengan WHERE clause yang sesuai.
Gunakan proper table joins jika perlu.
LIMIT 1000.

Jika hasil berisi id, sertakan kolom nama/alamat/deskripsi dengan JOIN ke tabel induk:
- pesantren_skor -> join pondok_pesantren untuk nama, alamat, kabupaten, provinsi
- santri -> join santri_pribadi untuk nama dan informasi lokasi/demografi
Tetap gunakan kolom yang ada di schema_context.json.

Generate SQL:"""
    
    @staticmethod
    def build_count_intent_prompt(query: str, entity: str) -> str:
        """Build optimized prompt untuk COUNT intent."""
        return f"""Intent: COUNT
Query: {query}
Entity: {entity}

Generate COUNT(*) query untuk {entity}.
Alias result column sebagai "total" atau "count".

Generate SQL:"""
    
    @staticmethod
    def build_statistics_intent_prompt(
        query: str,
        entities: List[str],
        agg_functions: Optional[List[str]] = None
    ) -> str:
        """Build optimized prompt untuk STATISTICS intent."""
        agg_str = ""
        if agg_functions:
            agg_str = f"\nUse aggregations: {', '.join(agg_functions)}"
        
        return f"""Intent: STATISTICS
Query: {query}
Entities: {', '.join(entities)}
{agg_str}

Generate aggregation query.
Include GROUP BY jika perlu.
Gunakan proper aliases untuk hasil.
LIMIT 1000.

Generate SQL:"""
    
    @staticmethod
    def build_ranking_intent_prompt(
        query: str,
        entity: str,
        sort_field: str,
        order: str = "DESC",
        limit: int = 10
    ) -> str:
        """Build optimized prompt untuk RANKING intent."""
        return f"""Intent: RANKING
Query: {query}
Entity: {entity}
Sort by: {sort_field}
Order: {order}
Limit: {limit}

Generate SELECT query dengan ORDER BY {sort_field} {order}.
LIMIT {limit}.

Generate SQL:"""
    
    @staticmethod
    def build_location_intent_prompt(query: str, entity: str) -> str:
        """Build optimized prompt untuk LOCATION intent."""
        return f"""Intent: LOCATION/HEATMAP
Query: {query}
Entity: {entity}

Generate SELECT query dengan geographic fields.
Include latitude, longitude, atau geometry fields.
Gunakan ST_X(), ST_Y() jika ada geometry column.
LIMIT 1000.

Generate SQL:"""
    
    @staticmethod
    def build_distance_intent_prompt(
        query: str,
        entity: str,
        center_lat: Optional[float] = None,
        center_lon: Optional[float] = None,
        radius_km: float = 10
    ) -> str:
        """Build optimized prompt untuk DISTANCE intent."""
        center_str = ""
        if center_lat and center_lon:
            center_str = f"\nCenter point: ({center_lat}, {center_lon})\nRadius: {radius_km} km"
        
        return f"""Intent: DISTANCE
Query: {query}
Entity: {entity}
{center_str}

Generate SELECT query dengan ST_DWithin untuk distance calculation.
Include distance dalam result.
Order by distance ASC.
LIMIT 100.

Generate SQL:"""
    
    @staticmethod
    def _format_schema(schema: Dict[str, Any]) -> str:
        """Format schema dict menjadi readable string."""
        schema_str = ""
        
        for table_name, table_info in schema.items():
            if isinstance(table_info, dict):
                schema_str += f"\nTable: {table_name}\n"
                
                if "columns" in table_info:
                    schema_str += "Columns:\n"
                    for col_name, col_info in table_info["columns"].items():
                        col_type = col_info.get("type", "unknown") if isinstance(col_info, dict) else col_info
                        schema_str += f"  - {col_name}: {col_type}\n"
                
                if "description" in table_info:
                    schema_str += f"Description: {table_info['description']}\n"
        
        return schema_str
    
    @staticmethod
    def build_clarification_prompt(
        original_query: str,
        error_message: str,
        attempted_sql: Optional[str] = None
    ) -> str:
        """Build prompt untuk meminta clarification ketika ada error."""
        clarification = f"""Seems ada masalah dengan previous query attempt.

Original query: {original_query}
Error: {error_message}"""
        
        if attempted_sql:
            clarification += f"\nPrevious SQL attempt: {attempted_sql}\n"
        
        clarification += """
Please try again with:
1. More specific field names
2. Clearer table references
3. Proper WHERE conditions

Generate SQL:"""
        
        return clarification
    
    @staticmethod
    def build_multi_step_prompt(
        user_query: str,
        detected_intents: List[str],
        required_steps: Optional[List[str]] = None
    ) -> str:
        """Build prompt untuk complex multi-step queries."""
        steps_str = ""
        if required_steps:
            steps_str = "Required steps:\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(required_steps, 1))
        
        return f"""Complex Query Analysis:
Query: {user_query}
Detected intents: {', '.join(detected_intents)}

{steps_str}

Generate SQL (atau multiple SQL statements jika perlu):"""
    
    @staticmethod
    def add_context_to_prompt(
        base_prompt: str,
        previous_context: Optional[List[Dict[str, str]]] = None,
        example_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Add conversation context ke prompt."""
        if previous_context:
            base_prompt += "\n\nPrevious queries in conversation:\n"
            for ctx in previous_context[-3:]:  # Last 3 for context
                base_prompt += f"- {ctx.get('query', '')}\n"
        
        if example_results:
            base_prompt += "\n\nExample result structures:\n"
            for result in example_results[:2]:  # Show 2 examples
                base_prompt += f"- {result}\n"
        
        return base_prompt
