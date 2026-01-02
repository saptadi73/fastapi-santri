#!/usr/bin/env python
"""Quick test of NL2SQL system without database."""

from app.nl2sql.intent_classifier import IntentClassifier

def test_intent_detection():
    """Test intent detection with various queries."""
    print("\n" + "="*70)
    print("INTENT DETECTION TEST")
    print("="*70 + "\n")
    
    test_cases = [
        ("Tunjukkan semua santri", "LIST"),
        ("Berapa jumlah santri?", "COUNT"),
        ("Santri miskin di Bandung", "FILTER"),
        ("Top 10 pesantren terbaik", "RANKING"),
        ("Peta distribusi santri", "LOCATION"),
        ("Rata-rata skor santri", "STATISTICS"),
    ]
    
    classifier = IntentClassifier()
    
    for query, expected_intent in test_cases:
        result = classifier.classify(query)
        status = "PASS" if result.intent.value.upper() == expected_intent else "WARN"
        
        print(f"[{status}] Query: {query}")
        print(f"       Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
        print(f"       Keywords: {', '.join(result.keywords) if result.keywords else 'None'}")
        print(f"       Expected: {expected_intent}")
        print()

if __name__ == "__main__":
    test_intent_detection()
    print("="*70)
    print("Test completed!")
    print("="*70 + "\n")
