"""
Direct test dari enricher functionality
"""
from app.core.database import SessionLocal
from app.nl2sql.result_enricher import ResultEnricher
from sqlalchemy import text

db = SessionLocal()
enricher = ResultEnricher(db)

# Simulate hasil query TOP 10 santri dengan score tertinggi
test_results = [
    {
        "santri_id": "ecaee84e-47e8-4645-ba55-f026e0b21a5e",
        "skor_total": 130
    },
    {
        "santri_id": "e000df55-dbd7-430e-a873-f84dd45d0726",
        "skor_total": 123
    }
]

print("=" * 80)
print("TESTING ENRICHER DIRECTLY")
print("=" * 80)

print("\nBefore enrichment:")
print(f"Fields: {list(test_results[0].keys())}")
print(f"Sample: {test_results[0]}\n")

# Test enrichment
enriched = enricher.enrich(
    test_results,
    "SELECT santri_id, skor_total FROM santri_skor ORDER BY skor_total DESC LIMIT 10"
)

print("After enrichment:")
print(f"Fields: {list(enriched[0].keys())}")
print(f"Sample: {enriched[0]}")

db.close()
