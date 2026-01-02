"""Test script untuk Output Normalizer dan Prompt Builder."""

from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from app.nl2sql.output_normalizer import OutputNormalizer
from app.nl2sql.prompt_builder import PromptBuilder
from app.nl2sql.intent_classifier import IntentClassifier, IntentResponse, IntentType


def test_output_normalizer():
    """Test OutputNormalizer dengan berbagai tipe data."""
    print("\n" + "="*70)
    print("TESTING OUTPUT NORMALIZER")
    print("="*70 + "\n")
    
    # Test data dengan berbagai tipe
    test_data = [
        {
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "nama": "Ahmad Hidayat",
            "skor": Decimal("85.50"),
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "birth_date": date(2009, 5, 20),
            "latitude": 6.9271,
            "longitude": 107.6062,
            "metadata": {
                "status": "aktif",
                "updated": datetime(2024, 1, 10, 15, 45, 0)
            }
        },
        {
            "id": UUID("87654321-4321-8765-4321-876543218765"),
            "nama": "Siti Nurhaliza",
            "skor": Decimal("92.75"),
            "created_at": datetime(2024, 1, 20, 14, 20, 0),
            "birth_date": date(2008, 8, 15),
            "latitude": 6.8852,
            "longitude": 107.5992,
            "metadata": None
        }
    ]
    
    # Test normalisasi
    normalized = OutputNormalizer.normalize_rows(test_data)
    
    print("Original data (first item):")
    print(f"  ID type: {type(test_data[0]['id']).__name__}")
    print(f"  Skor type: {type(test_data[0]['skor']).__name__}")
    print(f"  Created type: {type(test_data[0]['created_at']).__name__}")
    print(f"  Birth date type: {type(test_data[0]['birth_date']).__name__}")
    
    print("\nNormalized data (first item):")
    print(f"  ID: {normalized[0]['id']} (type: {type(normalized[0]['id']).__name__})")
    print(f"  Skor: {normalized[0]['skor']} (type: {type(normalized[0]['skor']).__name__})")
    print(f"  Created: {normalized[0]['created_at']}")
    print(f"  Birth date: {normalized[0]['birth_date']}")
    print(f"  Metadata null value: {normalized[0]['metadata']}")
    
    # Test format for different intents
    print("\n" + "-"*70)
    print("Testing format_for_response dengan berbagai intents:")
    print("-"*70 + "\n")
    
    # LIST intent
    list_response = OutputNormalizer.format_for_response(normalized, "list", include_count=True)
    if isinstance(list_response, dict):
        print(f"LIST intent response keys: {list_response.keys()}")
        print(f"  - data count: {len(list_response['data'])}")
        print(f"  - row count: {list_response['count']}")
    else:
        print(f"LIST intent response type: {type(list_response)}")
    
    # COUNT intent
    count_data = [{"total": 1234}]
    count_response = OutputNormalizer.format_for_response(count_data, "count")
    print(f"\nCOUNT intent response: {count_response}")
    
    # LOCATION intent
    location_response = OutputNormalizer.format_for_response(normalized, "location")
    if isinstance(location_response, dict):
        print(f"\nLOCATION intent response type: {location_response['type']}")
        print(f"  - features count: {len(location_response['features'])}")
        print(f"  - first feature: {location_response['features'][0]['geometry']}")
    else:
        print(f"\nLOCATION intent response type: {type(location_response)}")
    
    # Test JSON serializability
    print("\n" + "-"*70)
    print("JSON Serialization Test:")
    print("-"*70)
    print(f"Is JSON serializable: {OutputNormalizer.validate_json_serializable(normalized)}")


def test_prompt_builder():
    """Test PromptBuilder dengan berbagai intent."""
    print("\n" + "="*70)
    print("TESTING PROMPT BUILDER")
    print("="*70 + "\n")
    
    # Create sample schema
    sample_schema = {
        "santri_pribadi": {
            "description": "Tabel data pribadi santri",
            "columns": {
                "id": "UUID",
                "nama_santri": "VARCHAR",
                "usia": "INTEGER",
                "kategori_kemiskinan": "VARCHAR",
                "provinsi": "VARCHAR",
                "skor": "DECIMAL"
            }
        }
    }
    
    # Test system prompt
    print("1. SYSTEM PROMPT:\n")
    system_prompt = PromptBuilder.build_system_prompt(sample_schema)
    print(system_prompt[:300] + "...\n")
    
    # Create intent response
    classifier = IntentClassifier()
    intent = classifier.classify("Tunjukkan top 10 santri dengan skor tertinggi")
    
    # Test user prompt
    print("2. USER PROMPT:\n")
    user_prompt = PromptBuilder.build_user_prompt(
        "Tunjukkan top 10 santri dengan skor tertinggi",
        intent
    )
    print(user_prompt)
    
    # Test intent-specific prompts
    print("\n3. INTENT-SPECIFIC PROMPTS:\n")
    
    print("LIST Intent Prompt:")
    list_prompt = PromptBuilder.build_list_intent_prompt("Tunjukkan santri", "santri_pribadi")
    print(list_prompt)
    
    print("\nFILTER Intent Prompt:")
    filter_prompt = PromptBuilder.build_filter_intent_prompt(
        "Santri miskin di Jawa Barat",
        ["santri_pribadi"],
        ["kategori_kemiskinan = Miskin", "provinsi = Jawa Barat"]
    )
    print(filter_prompt)
    
    print("\nCOUNT Intent Prompt:")
    count_prompt = PromptBuilder.build_count_intent_prompt("Berapa santri?", "santri_pribadi")
    print(count_prompt)
    
    print("\nRANKING Intent Prompt:")
    ranking_prompt = PromptBuilder.build_ranking_intent_prompt(
        "Top 10 santri",
        "santri_pribadi",
        "skor",
        "DESC",
        10
    )
    print(ranking_prompt)
    
    print("\nLOCATION Intent Prompt:")
    location_prompt = PromptBuilder.build_location_intent_prompt(
        "Peta santri",
        "santri_pribadi"
    )
    print(location_prompt)
    
    print("\nDISTANCE Intent Prompt:")
    distance_prompt = PromptBuilder.build_distance_intent_prompt(
        "Santri dekat Bandung",
        "santri_pribadi",
        -6.9271,
        107.6062,
        10
    )
    print(distance_prompt)


def test_integration():
    """Test integration antara OutputNormalizer, PromptBuilder, dan Intent Classifier."""
    print("\n" + "="*70)
    print("TESTING INTEGRATION")
    print("="*70 + "\n")
    
    # Step 1: Detect intent
    classifier = IntentClassifier()
    query = "Top 10 pesantren terbaik di Jawa Barat"
    intent = classifier.classify(query)
    
    print(f"User Query: {query}")
    print(f"Detected Intent: {intent.intent.value}")
    print(f"Confidence: {intent.confidence:.2%}")
    print(f"Entities: {', '.join(intent.entity_types)}\n")
    
    # Step 2: Build appropriate prompt
    if intent.intent == IntentType.RANKING:
        prompt = PromptBuilder.build_ranking_intent_prompt(
            query,
            "pondok_pesantren",
            "skor_keseluruhan",
            "DESC",
            10
        )
        print("Generated Prompt for OpenAI:")
        print(prompt)
    
    # Step 3: Simulate database results
    mock_results = [
        {
            "id": "uuid-1",
            "nama_pesantren": "Pesantren Al-Azhar",
            "skor_keseluruhan": Decimal("95.5"),
            "provinsi": "Jawa Barat",
            "created_at": datetime.now()
        },
        {
            "id": "uuid-2",
            "nama_pesantren": "Pesantren Darul Qur'an",
            "skor_keseluruhan": Decimal("92.3"),
            "provinsi": "Jawa Barat",
            "created_at": datetime.now()
        }
    ]
    
    # Step 4: Normalize output
    print("\nDatabase Results (before normalization):")
    print(f"  Skor type: {type(mock_results[0]['skor_keseluruhan']).__name__}")
    
    normalized = OutputNormalizer.format_for_response(mock_results, "ranking")
    
    print("\nNormalized Output (ready for API response):")
    if isinstance(normalized, dict) and 'data' in normalized:
        print(f"  Skor type: {type(normalized['data'][0]['skor_keseluruhan']).__name__}")
        print(f"  Data: {normalized['data']}")
        print(f"  Count: {normalized['count']}")
    else:
        print(f"  Type: {type(normalized)}")


if __name__ == "__main__":
    try:
        test_output_normalizer()
        test_prompt_builder()
        test_integration()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()
