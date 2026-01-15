"""
Diversify GPS locations by adding random variations within 2-5 km radius
Uses Haversine formula to calculate new points within specified radius
"""
import random
import math
from app.core.database import engine
from sqlalchemy import text
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Point

def haversine_random_point(lon, lat, min_km=2, max_km=5):
    """
    Generate a random point within a specified radius (in km)
    Returns: (new_lon, new_lat)
    """
    # Earth's radius in km
    R = 6371
    
    # Random distance between min_km and max_km
    distance = random.uniform(min_km, max_km)
    
    # Random bearing (0-360 degrees)
    bearing = random.uniform(0, 360)
    
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing)
    distance_rad = distance / R
    
    # Calculate new position
    new_lat = math.asin(
        math.sin(lat_rad) * math.cos(distance_rad) +
        math.cos(lat_rad) * math.sin(distance_rad) * math.cos(bearing_rad)
    )
    
    new_lon = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_rad) * math.cos(lat_rad),
        math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat)
    )
    
    # Convert back to degrees
    return (math.degrees(new_lon), math.degrees(new_lat))


def diversify_locations():
    """Add random variations to duplicate locations"""
    with engine.begin() as connection:
        try:
            # Get all santri with coordinates, grouped by location
            result = connection.execute(
                text("""
                    SELECT 
                        id, 
                        ST_X(lokasi) as lon, 
                        ST_Y(lokasi) as lat,
                        ROW_NUMBER() OVER (PARTITION BY ST_X(lokasi), ST_Y(lokasi) ORDER BY id) as row_num
                    FROM santri_pribadi 
                    WHERE lokasi IS NOT NULL
                    ORDER BY ST_X(lokasi), ST_Y(lokasi), id
                """)
            )
            
            updates = []
            for row in result:
                santri_id, lon, lat, row_num = row
                
                # Keep the first one at original location, diversify the rest
                if row_num > 1:
                    new_lon, new_lat = haversine_random_point(lon, lat, min_km=2, max_km=5)
                    updates.append({
                        'id': str(santri_id),
                        'lon': new_lon,
                        'lat': new_lat,
                        'orig_lon': lon,
                        'orig_lat': lat
                    })
            
            print("=" * 80)
            print("DIVERSIFYING GPS LOCATIONS")
            print("=" * 80)
            print(f"\nTotal santri to update: {len(updates)}")
            
            # Apply updates
            success_count = 0
            for update in updates:
                try:
                    connection.execute(
                        text("""
                            UPDATE santri_pribadi 
                            SET lokasi = ST_Point(:lon, :lat, 4326)
                            WHERE id = :id
                        """),
                        {
                            'lon': update['lon'],
                            'lat': update['lat'],
                            'id': update['id']
                        }
                    )
                    success_count += 1
                    
                    if success_count <= 5 or success_count % 50 == 0:
                        dist_km = math.sqrt(
                            (update['lon'] - update['orig_lon'])**2 +
                            (update['lat'] - update['orig_lat'])**2
                        ) * 111  # Rough km conversion
                        print(f"✓ Updated {success_count}/{len(updates)} - "
                              f"({update['orig_lon']:.4f}, {update['orig_lat']:.4f}) → "
                              f"({update['lon']:.4f}, {update['lat']:.4f}) [~{dist_km:.2f}km]")
                    
                except Exception as e:
                    print(f"✗ Failed to update {update['id']}: {e}")
            
            print(f"\n✓ Successfully updated {success_count} santri locations")
            
            # Verify
            result = connection.execute(
                text("""
                    SELECT 
                        COUNT(*) as count_coords
                    FROM santri_pribadi 
                    WHERE lokasi IS NOT NULL
                """)
            )
            count_coords = result.scalar()
            
            result = connection.execute(
                text("""
                    SELECT 
                        COUNT(DISTINCT ST_AsText(lokasi)) as unique_locations
                    FROM santri_pribadi 
                    WHERE lokasi IS NOT NULL
                """)
            )
            unique_locs = result.scalar()
            
            print(f"\nVerification:")
            print(f"  Total santri with coordinates: {count_coords}")
            print(f"  Unique locations: {unique_locs}")
            print(f"  Average santri per location: {count_coords / unique_locs:.1f}")
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    diversify_locations()
