"""
Diversify pesantren GPS locations with wider radius (10-35 km)
For broader geographic distribution
"""
import random
import math
from app.core.database import engine
from sqlalchemy import text

def haversine_random_point(lon, lat, min_km=10, max_km=35):
    """Generate random point within specified radius (10-35 km)"""
    R = 6371  # Earth's radius in km
    distance = random.uniform(min_km, max_km)
    bearing = random.uniform(0, 360)
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing)
    distance_rad = distance / R
    
    new_lat = math.asin(
        math.sin(lat_rad) * math.cos(distance_rad) +
        math.cos(lat_rad) * math.sin(distance_rad) * math.cos(bearing_rad)
    )
    
    new_lon = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_rad) * math.cos(lat_rad),
        math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat)
    )
    
    return (math.degrees(new_lon), math.degrees(new_lat))


def diversify_pesantren_wide():
    """Add wide-range variations to ALL pesantren locations (10-35 km)"""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text("""
                    SELECT 
                        id, 
                        nama,
                        ST_X(lokasi) as lon, 
                        ST_Y(lokasi) as lat
                    FROM pondok_pesantren 
                    WHERE lokasi IS NOT NULL
                    ORDER BY id
                """)
            )
            
            updates = []
            orig_locs = {}
            for row in result:
                pesantren_id, nama, lon, lat = row
                orig_locs[str(pesantren_id)] = (lon, lat)
                new_lon, new_lat = haversine_random_point(lon, lat, min_km=10, max_km=35)
                updates.append({
                    'id': str(pesantren_id),
                    'nama': nama,
                    'lon': new_lon,
                    'lat': new_lat,
                    'orig_lon': lon,
                    'orig_lat': lat
                })
            
            print("=" * 80)
            print("DIVERSIFYING PESANTREN GPS LOCATIONS (10-35 KM RADIUS)")
            print("=" * 80)
            print(f"\nTotal pesantren to update: {len(updates)}")
            
            success_count = 0
            total_distance = 0
            
            for update in updates:
                try:
                    connection.execute(
                        text("""
                            UPDATE pondok_pesantren 
                            SET lokasi = ST_Point(:lon, :lat, 4326)
                            WHERE id = :id
                        """),
                        {'lon': update['lon'], 'lat': update['lat'], 'id': update['id']}
                    )
                    
                    # Calculate distance
                    dist_km = math.sqrt(
                        (update['lon'] - update['orig_lon'])**2 +
                        (update['lat'] - update['orig_lat'])**2
                    ) * 111  # Rough conversion to km
                    total_distance += dist_km
                    
                    success_count += 1
                    
                    if success_count <= 5 or success_count % 100 == 0 or success_count == len(updates):
                        print(f"✓ Updated {success_count}/{len(updates)} - {update['nama'][:40]}: "
                              f"({update['orig_lon']:.3f}, {update['orig_lat']:.3f}) → "
                              f"({update['lon']:.3f}, {update['lat']:.3f}) [~{dist_km:.1f}km]")
                
                except Exception as e:
                    print(f"✗ Failed for {update['nama']}: {e}")
            
            avg_distance = total_distance / success_count if success_count > 0 else 0
            print(f"\n✓ Successfully updated {success_count} pesantren locations")
            print(f"  Average distance from original: {avg_distance:.1f} km")
            
            # Verify
            result = connection.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(DISTINCT ST_AsText(lokasi)) as unique_locations
                    FROM pondok_pesantren 
                    WHERE lokasi IS NOT NULL
                """)
            )
            total, unique_locs = result.fetchone()
            
            print(f"\nVerification:")
            print(f"  Total pesantren: {total}")
            print(f"  Unique locations: {unique_locs}")
            print(f"  Diversification: {(unique_locs/total)*100:.1f}%")
            print("=" * 80)
            
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    diversify_pesantren_wide()
