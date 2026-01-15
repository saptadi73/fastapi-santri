"""
Diversify pesantren GPS locations with aggressive variation
Apply to ALL locations including original cluster centers
"""
import random
import math
from app.core.database import engine
from sqlalchemy import text

def haversine_random_point(lon, lat, min_km=2, max_km=5):
    """Generate random point within specified radius"""
    R = 6371
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


def diversify_pesantren():
    """Add variations to ALL pesantren locations"""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text("""
                    SELECT 
                        id, 
                        ST_X(lokasi) as lon, 
                        ST_Y(lokasi) as lat
                    FROM pondok_pesantren 
                    WHERE lokasi IS NOT NULL
                    ORDER BY id
                """)
            )
            
            updates = []
            for row in result:
                pesantren_id, lon, lat = row
                new_lon, new_lat = haversine_random_point(lon, lat, min_km=0.5, max_km=5)
                updates.append({
                    'id': str(pesantren_id),
                    'lon': new_lon,
                    'lat': new_lat
                })
            
            print("=" * 80)
            print("DIVERSIFYING PESANTREN GPS LOCATIONS")
            print("=" * 80)
            print(f"\nTotal pesantren to update: {len(updates)}")
            
            success_count = 0
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
                    success_count += 1
                    
                    if success_count % 100 == 0 or success_count == len(updates):
                        print(f"✓ Updated {success_count}/{len(updates)}")
                
                except Exception as e:
                    print(f"✗ Failed: {e}")
            
            print(f"\n✓ Successfully updated {success_count} pesantren locations")
            
            # Verify
            result = connection.execute(
                text("""
                    SELECT 
                        COUNT(DISTINCT ST_AsText(lokasi)) as unique_locations
                    FROM pondok_pesantren 
                    WHERE lokasi IS NOT NULL
                """)
            )
            unique_locs = result.scalar()
            print(f"\nResult: Now have {unique_locs} unique locations")
            print(f"Previous: 17 clusters → Current: {unique_locs} unique")
            print("=" * 80)
            
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    diversify_pesantren()
