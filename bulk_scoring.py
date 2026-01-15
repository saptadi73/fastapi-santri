"""
Bulk Scoring Script
Recalculate all santri and pesantren scores at once
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def recalculate_all_santri():
    """Recalculate scores for all santri"""
    print("=" * 70)
    print("RECALCULATING ALL SANTRI SCORES")
    print("=" * 70)
    
    url = f"{BASE_URL}/api/scoring/batch/calculate-all"
    
    print(f"\nPOST {url}")
    print("Processing...")
    
    start_time = time.time()
    response = requests.post(url)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ SUCCESS ({elapsed:.2f}s)")
        print(f"  Total Processed: {data['data']['total_processed']}")
        print(f"  Total Errors: {data['data']['total_errors']}")
        
        if data['data']['errors']:
            print("\n  Errors:")
            for error in data['data']['errors'][:5]:  # Show first 5 errors
                print(f"    - {error['nama']} ({error['santri_id']}): {error['error']}")
            if len(data['data']['errors']) > 5:
                print(f"    ... and {len(data['data']['errors']) - 5} more errors")
        
        return data['data']
    else:
        print(f"\n✗ FAILED ({response.status_code})")
        print(f"  {response.text}")
        return None


def recalculate_all_pesantren():
    """Recalculate scores for all pesantren"""
    print("\n" + "=" * 70)
    print("RECALCULATING ALL PESANTREN SCORES")
    print("=" * 70)
    
    url = f"{BASE_URL}/api/pesantren-scoring/batch/calculate-all"
    
    print(f"\nPOST {url}")
    print("Processing...")
    
    start_time = time.time()
    response = requests.post(url)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ SUCCESS ({elapsed:.2f}s)")
        print(f"  Total Processed: {data['data']['total_processed']}")
        print(f"  Total Errors: {data['data']['total_errors']}")
        
        if data['data']['errors']:
            print("\n  Errors:")
            for error in data['data']['errors'][:5]:  # Show first 5 errors
                print(f"    - {error['nama']} ({error['pesantren_id']}): {error['error']}")
            if len(data['data']['errors']) > 5:
                print(f"    ... and {len(data['data']['errors']) - 5} more errors")
        
        return data['data']
    else:
        print(f"\n✗ FAILED ({response.status_code})")
        print(f"  {response.text}")
        return None


def main():
    """Run both bulk scoring operations"""
    print("\n🚀 BULK SCORING - Recalculate All Scores")
    print("Make sure your FastAPI server is running on http://localhost:8000\n")
    
    total_start = time.time()
    
    # Recalculate santri scores
    santri_result = recalculate_all_santri()
    
    # Recalculate pesantren scores
    pesantren_result = recalculate_all_pesantren()
    
    # Summary
    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if santri_result:
        print(f"✓ Santri: {santri_result['total_processed']} processed, {santri_result['total_errors']} errors")
    else:
        print("✗ Santri: Failed to process")
    
    if pesantren_result:
        print(f"✓ Pesantren: {pesantren_result['total_processed']} processed, {pesantren_result['total_errors']} errors")
    else:
        print("✗ Pesantren: Failed to process")
    
    print(f"\nTotal Time: {total_elapsed:.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n\n✗ ERROR: Cannot connect to server at http://localhost:8000")
        print("   Make sure your FastAPI server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
