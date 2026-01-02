"""
Test script for NL2SQL Intent Classification and SQL Generation System.
Run this to verify the entire pipeline is working.
"""

import json
import time
from app.nl2sql.intent_classifier import IntentClassifier, IntentType
from app.nl2sql.nl2sql_service import NL2SQLService
from app.core.database import SessionLocal

def test_intent_classifier():
    """Test intent classification with various queries."""
    print("\n" + "="*70)
    print("TESTING INTENT CLASSIFIER")
    print("="*70)
    
    test_queries = [
        "Tunjukkan semua santri",
        "Berapa jumlah santri di Jawa Barat?",
        "Pesantren mana yang terbaik?",
        "Santri miskin dengan skor tertinggi di Bandung",
        "Peta distribusi santri kemiskinan",
        "Pesantren terdekat dari lokasi ini",
        "Top 10 santri dengan nilai bagus",
        "Statistik kategori kemiskinan santri",
        "Simpan data santri baru",  # Should be UNKNOWN
        "Halo",  # Should be HELP or UNKNOWN
    ]
    
    classifier = IntentClassifier()
    
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"  Intent: {result.intent.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Keywords: {', '.join(result.keywords) if result.keywords else 'None'}")
        print(f"  Entity Types: {', '.join(result.entity_types) if result.entity_types else 'None'}")


def test_nl2sql_service():
    """Test NL2SQL service with actual database queries."""
    print("\n" + "="*70)
    print("TESTING NL2SQL SERVICE")
    print("="*70)
    
    db = SessionLocal()
    service = NL2SQLService(db)
    
    test_queries = [
        "Tunjukkan 5 santri terbaru",
        "Berapa jumlah santri?",
        "Top 10 pesantren dengan skor tertinggi",
        "Santri di kategori kemiskinan sangat miskin",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = service.process_query(query)
            execution_time = (time.time() - start_time) * 1000
            
            if result.get("error"):
                print(f"ERROR: {result['error']}")
            else:
                intent = result["intent"]
                print(f"Intent: {intent.intent.value} (confidence: {intent.confidence:.2f})")
                print(f"SQL: {result['sql_query'][:100]}...")
                print(f"Results: {len(result['result'])} rows")
                print(f"Execution Time: {execution_time:.2f}ms")
                
                # Show first row if available
                if result["result"]:
                    print(f"First row: {str(result['result'][0])[:80]}...")
                    
        except Exception as e:
            print(f"ERROR: {str(e)}")
        finally:
            print("-" * 50)
    
    db.close()


def test_schema_context():
    """Test schema context is loaded correctly."""
    print("\n" + "="*70)
    print("TESTING SCHEMA CONTEXT")
    print("="*70)
    
    db = SessionLocal()
    service = NL2SQLService(db)
    
    try:
        # load_schema_context is a module-level function, not a method
        from app.nl2sql.nl2sql_service import load_schema_context
        schema = load_schema_context()
        print(f"Schema context loaded successfully")
        print(f"Tables: {', '.join(schema.keys())}")
        print(f"Total tables: {len(schema.keys())}")
        
        # Show sample table structure
        if "pondok_pesantren" in schema:
            print(f"\nSample table (pondok_pesantren):")
            print(json.dumps(schema["pondok_pesantren"], indent=2, ensure_ascii=False)[:500] + "...")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()


def test_sql_validation():
    """Test SQL validation rules."""
    print("\n" + "="*70)
    print("TESTING SQL VALIDATION")
    print("="*70)
    
    db = SessionLocal()
    service = NL2SQLService(db)
    
    test_cases = [
        ("SELECT * FROM santri LIMIT 100", True, "Valid SELECT"),
        ("DELETE FROM santri WHERE id = 1", False, "Dangerous DELETE"),
        ("DROP TABLE santri", False, "Dangerous DROP"),
        ("UPDATE santri SET nama = 'Test'", False, "Dangerous UPDATE"),
        ("SELECT * FROM santri", False, "Missing LIMIT"),
        ("SELECT * FROM santri LIMIT 2000", False, "LIMIT too high"),
    ]
    
    for sql, should_pass, description in test_cases:
        validation = service.validate_sql(sql)
        status = "PASS" if (validation["is_valid"] == should_pass) else "FAIL"
        print(f"{status}: {description}")
        print(f"  SQL: {sql}")
        print(f"  Valid: {validation['is_valid']}, Error: {validation['error']}")
        print()
    
    db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NL2SQL SYSTEM TEST SUITE")
    print("="*70)
    
    # Test 1: Intent Classifier
    test_intent_classifier()
    
    # Test 2: Schema Context
    test_schema_context()
    
    # Test 3: SQL Validation
    test_sql_validation()
    
    # Test 4: Full NL2SQL Pipeline
    test_nl2sql_service()
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETED")
    print("="*70 + "\n")
