"""
Analyze duplicate GPS locations in santri_pribadi
"""
from app.core.database import engine
from sqlalchemy import text
from collections import defaultdict

def analyze_duplicate_locations():
    """Analyze which santri have the same or very close GPS locations"""
    with engine.connect() as conn:
        # Get all santri with coordinates
        result = conn.execute(
            text("""
                SELECT 
                    id, nama, 
                    ST_X(lokasi) as lon, 
                    ST_Y(lokasi) as lat,
                    COUNT(*) OVER (PARTITION BY ST_X(lokasi), ST_Y(lokasi)) as count_same_loc
                FROM santri_pribadi 
                WHERE lokasi IS NOT NULL
                ORDER BY count_same_loc DESC, ST_X(lokasi), ST_Y(lokasi)
            """)
        )
        
        locations = defaultdict(list)
        for row in result:
            santri_id, nama, lon, lat, count = row
            key = (round(lon, 6), round(lat, 6))  # Group by rounded coordinates
            locations[key].append({
                'id': str(santri_id),
                'nama': nama,
                'lon': lon,
                'lat': lat,
                'same_count': count
            })
        
        print("=" * 80)
        print("DUPLICATE GPS LOCATIONS ANALYSIS")
        print("=" * 80)
        
        # Show duplicates
        duplicates_count = 0
        for loc, santris in locations.items():
            if len(santris) > 1:
                duplicates_count += len(santris)
                print(f"\n📍 Location: {loc}")
                print(f"   Santri count: {len(santris)}")
                for santri in santris[:3]:  # Show first 3
                    print(f"   - {santri['nama']} ({santri['lon']}, {santri['lat']})")
                if len(santris) > 3:
                    print(f"   ... and {len(santris) - 3} more")
        
        print(f"\n" + "=" * 80)
        print(f"Total unique locations: {len(locations)}")
        print(f"Total santri with duplicate locations: {duplicates_count}")
        print(f"Total santri with unique locations: {len(locations) - sum(1 for s in locations.values() if len(s) > 1)}")
        print("=" * 80)
        
        return locations

if __name__ == "__main__":
    analyze_duplicate_locations()
