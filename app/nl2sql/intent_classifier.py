"""Intent classifier for NL2SQL - identifies query type."""

from enum import Enum
from pydantic import BaseModel
from typing import Optional


class IntentType(str, Enum):
    """Supported query intents."""
    # Data Retrieval
    LIST = "list"  # Ambil data santri, pesantren, dll
    FILTER = "filter"  # Filter berdasarkan kondisi
    COUNT = "count"  # Hitung jumlah
    
    # Analysis
    STATISTICS = "statistics"  # Statistik, agregasi, rata-rata
    TREND = "trend"  # Trend, perbandingan waktu
    RANKING = "ranking"  # Rank/sorting
    
    # GIS/Location
    LOCATION = "location"  # Query berbasis lokasi
    DISTANCE = "distance"  # Radius/jarak
    HEATMAP = "heatmap"  # Data untuk heatmap
    
    # Scoring
    SCORING = "scoring"  # Score santri/pesantren
    CATEGORY = "category"  # Kategori berdasarkan score
    
    # Other
    UNKNOWN = "unknown"
    HELP = "help"


class IntentResponse(BaseModel):
    """Response from intent classifier."""
    intent: IntentType
    confidence: float  # 0.0-1.0
    keywords: list[str]  # Keywords found
    entity_types: list[str]  # Types of entities (santri, pesantren, etc)
    description: str  # Plain English description


class IntentClassifier:
    """Classify user queries into intents."""
    
    # Keywords untuk setiap intent
    INTENT_KEYWORDS = {
        IntentType.LIST: {
            "keywords": ["tunjukkan", "tampilkan", "lihat", "daftar", "list", "semua", 
                        "siapa saja", "berapa banyak orang", "data"],
            "synonyms": ["tampilkan list", "ambil data", "lihat semua"]
        },
        IntentType.FILTER: {
            "keywords": ["filter", "dimana", "yang mana", "dengan", "dari", "di", 
                        "provinsi", "kabupaten", "pesantren", "status", "kategori"],
            "synonyms": ["cari yang", "temukan", "sebutkan"]
        },
        IntentType.COUNT: {
            "keywords": ["berapa", "jumlah", "total", "banyak", "ada berapa", "hitung"],
            "synonyms": ["hitunglah", "hitung total"]
        },
        IntentType.STATISTICS: {
            "keywords": ["statistik", "rata-rata", "average", "mean", "median", "mode", 
                        "distribusi", "persentase", "analisis", "summary"],
            "synonyms": ["berapa rata-rata", "apa distribusi", "analisis"]
        },
        IntentType.TREND: {
            "keywords": ["trend", "perbandingan", "vs", "versus", "bandingkan", "naik", 
                        "turun", "berkembang", "progress", "pertumbuhan"],
            "synonyms": ["dibanding", "compared to", "lebih tinggi"]
        },
        IntentType.RANKING: {
            "keywords": ["ranking", "urutan", "terbaik", "terburuk", "tertinggi", 
                        "terendah", "top", "bottom", "rank", "sort"],
            "synonyms": ["urutkan", "sortir", "top 10"]
        },
        IntentType.LOCATION: {
            "keywords": ["lokasi", "dimana", "letak", "peta", "map", "koordinat", 
                        "lat", "lon", "latitude", "longitude"],
            "synonyms": ["di mana", "location", "tempat"]
        },
        IntentType.DISTANCE: {
            "keywords": ["dekat", "jauh", "radius", "jarak", "km", "meter", "dalam jarak",
                        "sekitar", "terdekat", "nearest"],
            "synonyms": ["dalam radius", "sejauh", "berjarak"]
        },
        IntentType.HEATMAP: {
            "keywords": ["heatmap", "kepadatan", "distribusi spasial", "konsentrasi",
                        "peta panas", "visualisasi", "intensity"],
            "synonyms": ["density map", "spatial distribution"]
        },
        IntentType.SCORING: {
            "keywords": ["skor", "score", "nilai", "rating", "penilaian", "evaluasi",
                        "kelayakan", "kemiskinan"],
            "synonyms": ["berapa nilai", "apa scorenya", "penilaian"]
        },
        IntentType.CATEGORY: {
            "keywords": ["kategori", "kategri", "class", "golongan", "jenis", "tipe",
                        "sangat miskin", "miskin", "rentan", "tidak miskin",
                        "sangat layak", "layak", "cukup layak", "tidak layak"],
            "synonyms": ["masuk kategori", "termasuk apa"]
        },
        IntentType.HELP: {
            "keywords": ["help", "bantuan", "cara", "bagaimana", "gimana", "tanya",
                        "apa itu", "bisa apa", "fitur apa"],
            "synonyms": ["tolong", "jelaskan", "sebutkan fitur"]
        }
    }
    
    # Entity types
    ENTITY_KEYWORDS = {
        "santri": ["santri", "murid", "siswa", "peserta didik", "pelajar"],
        "pesantren": ["pesantren", "ponpes", "pondok", "madrasah", "sekolah"],
        "orangtua": ["orangtua", "orang tua", "ayah", "ibu", "wali", "orang"],
        "rumah": ["rumah", "tempat tinggal", "hunian", "domisili", "alamat"],
        "aset": ["aset", "barang", "motor", "mobil", "hp", "harta", "properti"],
        "kesehatan": ["kesehatan", "gizi", "berat", "tinggi", "kesehatan"],
        "pembiayaan": ["biaya", "pembayaran", "pembiayaan", "uang", "donasi", "beasiswa"],
        "lokasi": ["lokasi", "tempat", "letak", "peta", "koordinat", "alamat"],
        "score": ["skor", "nilai", "rating", "penilaian", "score", "kelayakan"],
    }
    
    @classmethod
    def classify(cls, query: str) -> IntentResponse:
        """
        Classify user query into intent.
        
        Args:
            query: Natural language query from user
            
        Returns:
            IntentResponse with detected intent and metadata
        """
        query_lower = query.lower()
        
        # Find matched keywords and calculate confidence
        intent_scores = {}
        matched_keywords_all = []
        
        for intent_type, intent_data in cls.INTENT_KEYWORDS.items():
            keywords = intent_data["keywords"]
            synonyms = intent_data.get("synonyms", [])
            all_keywords = keywords + synonyms
            
            # Count matched keywords
            matched = [kw for kw in all_keywords if kw in query_lower]
            matched_keywords_all.extend(matched)
            
            if matched:
                # Confidence = matched keywords / total keywords
                confidence = len(matched) / len(all_keywords)
                intent_scores[intent_type] = confidence
        
        # Determine best intent
        if not intent_scores:
            best_intent = IntentType.UNKNOWN
            confidence = 0.0
        else:
            best_intent: IntentType = max(intent_scores, key=intent_scores.get)  # type: ignore
            confidence = intent_scores[best_intent]
        
        # Find entity types
        detected_entities = []
        for entity, keywords in cls.ENTITY_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                detected_entities.append(entity)
        
        # Generate description
        description = f"User menanyakan tentang {best_intent.value}"
        if detected_entities:
            description += f" untuk {', '.join(detected_entities)}"
        
        return IntentResponse(
            intent=best_intent,
            confidence=min(confidence, 1.0),
            keywords=list(set(matched_keywords_all)),  # Unique keywords
            entity_types=detected_entities,
            description=description
        )


# Test examples
if __name__ == "__main__":
    test_queries = [
        "Tunjukkan semua santri di Jawa Barat",
        "Berapa jumlah santri miskin?",
        "Pesantren mana yang terbaik?",
        "Heatmap distribusi santri kemiskinan",
        "Santri dengan score tertinggi siapa?",
        "Bantuan untuk query",
    ]
    
    classifier = IntentClassifier()
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
        print(f"Keywords: {result.keywords}")
        print(f"Entities: {result.entity_types}")
        print(f"Description: {result.description}")
