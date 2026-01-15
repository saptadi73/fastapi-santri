"""
More aggressive diversification - add variations to ALL locations including the original cluster center
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


def aggressive_diversify():
    """Add variations to ALL locations"""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text("""
                    SELECT 
                        id, 
                        ST_X(lokasi) as lon, 
                        ST_Y(lokasi) as lat
                    FROM santri_pribadi 
                    WHERE lokasi IS NOT NULL
                    ORDER BY id
                """)
            )
            
            updates = []
            for row in result:
                santri_id, lon, lat = row
                # Add variation to ALL locations
                new_lon, new_lat = haversine_random_point(lon, lat, min_km=0.5, max_km=5)
                updates.append({
                    'id': str(santri_id),
                    'lon': new_lon,
                    'lat': new_lat
                })
            
            print("=" * 80)
            print("AGGRESSIVE GPS DIVERSIFICATION (All Locations)")
            print("=" * 80)
            print(f"\nTotal santri to update: {len(updates)}")
            
            success_count = 0
            for update in updates:
                try:
                    connection.execute(
                        text("""
                            UPDATE santri_pribadi 
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
            
            print(f"\n✓ Successfully updated {success_count} santri locations")
            
            # Verify
            result = connection.execute(
                text("""
                    SELECT 
                        COUNT(DISTINCT ST_AsText(lokasi)) as unique_locations
                    FROM santri_pribadi 
                    WHERE lokasi IS NOT NULL
                """)
            )
            unique_locs = result.scalar()
            print(f"\nResult: Now have {unique_locs} unique locations (was 18 clusters)")
            print("=" * 80)
            
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    aggressive_diversify()
