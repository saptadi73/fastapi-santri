"""Test breakdown scoring"""
import sys
import json
from uuid import UUID

try:
    # Import main app first to ensure all models are loaded
    from app.main import app
    
    from app.core.database import SessionLocal
    from app.services.score_service import ScoreService
    
    print("✓ Imports successful")
    
    db = SessionLocal()
    service = ScoreService(db)
    
    print("✓ Service created")
    
    santri_id = UUID('ae739ebe-2f19-43e1-9244-580bfb8a9acf')
    result = service.get_by_santri_id(santri_id)
    
    if result:
        record, breakdown = result
        print("\n=== BREAKDOWN RESULT ===")
        print(json.dumps(breakdown, indent=2, default=str))
        print(f"\nTotal Score: {record.skor_total}")
        print(f"Category: {record.kategori_kemiskinan}")
    else:
        print("No score found")
    
    db.close()
    print("\n✓ Test completed successfully")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
