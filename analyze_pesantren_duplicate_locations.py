"""
Analyze duplicate GPS locations in pondok_pesantren
"""
from app.core.database import engine
from sqlalchemy import text
from collections import defaultdict

def analyze_pesantren_locations():
    """Analyze which pesantren have the same GPS locations"""
    with engine.connect() as conn:
        # Get all pesantren with coordinates
        result = conn.execute(
            text("""
                SELECT 
                    id, nama, 
                    ST_X(lokasi) as lon, 
                    ST_Y(lokasi) as lat,
                    COUNT(*) OVER (PARTITION BY ST_X(lokasi), ST_Y(lokasi)) as count_same_loc
                FROM pondok_pesantren 
                WHERE lokasi IS NOT NULL
                ORDER BY count_same_loc DESC, ST_X(lokasi), ST_Y(lokasi)
            """)
        )
        
        locations = defaultdict(list)
        for row in result:
            pesantren_id, nama, lon, lat, count = row
            key = (round(lon, 6), round(lat, 6))
            locations[key].append({
                'id': str(pesantren_id),
                'nama': nama,
                'lon': lon,
                'lat': lat
            })
        
        print("=" * 80)
        print("PESANTREN GPS LOCATIONS ANALYSIS")
        print("=" * 80)
        
        # Show duplicates
        duplicates_count = 0
        duplicate_clusters = []
        for loc, pesantrens in locations.items():
            if len(pesantrens) > 1:
                duplicates_count += len(pesantrens)
                duplicate_clusters.append({
                    'location': loc,
                    'count': len(pesantrens),
                    'pesantrens': pesantrens
                })
        
        # Sort by count
        duplicate_clusters.sort(key=lambda x: x['count'], reverse=True)
        
        for cluster in duplicate_clusters:
            print(f"\nLocation: {cluster['location']}")
            print(f"  Count: {cluster['count']}")
            for p in cluster['pesantrens'][:3]:
                print(f"  - {p['nama']}")
            if len(cluster['pesantrens']) > 3:
                print(f"  ... and {len(cluster['pesantrens']) - 3} more")
        
        print(f"\n" + "=" * 80)
        print(f"Total unique locations: {len(locations)}")
        print(f"Total pesantren with duplicate locations: {duplicates_count}")
        unique_loc_count = len(locations) - len(duplicate_clusters)
        print(f"Total pesantren with unique locations: {unique_loc_count}")
        print("=" * 80)
        
        return locations

if __name__ == "__main__":
    analyze_pesantren_locations()
