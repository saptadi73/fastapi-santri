# GPS Location Diversification Guide

## Overview

Dummy data santri_pribadi sebelumnya memiliki 400 santri dengan lokasi yang sama atau sangat berdekatan (18 cluster utama). Saat ini, semua 403 santri telah didiversifikasi dengan koordinat GPS unik yang tersebar dalam radius 0.5-5 km dari lokasi cluster asli.

## Results

✅ **Status: 100% Complete**
- Total Santri: 403
- Unique GPS Locations: 403 (sebelumnya hanya 18 cluster)
- Diversification Method: Haversine formula dengan random bearing dan jarak
- Radius Applied: 0.5-5 km per santri

## Scripts Used

### 1. `diversify_gps_locations.py`
Diversifikasi pertama - keep original cluster center, varies the rest:
- Kept 18 original locations (cluster centers)
- Added variation to 385 santri (2-5 km radius)
- Result: ~22 santri per location

```bash
python diversify_gps_locations.py
```

### 2. `aggressive_diversify_gps.py`
Diversifikasi agresif - adds variation to ALL locations:
- Applied random variation to all 403 santri
- Range: 0.5-5 km radius per point
- Result: 403 unique locations

```bash
python aggressive_diversify_gps.py
```

## Sample Diversified Locations

Before:
```
400+ santri with only 18 clusters:
- 57 santri at (113.7030, -8.1670)
- 51 santri at (112.6150, -7.9460)
- 42 santri at (112.7370, -7.2750)
... etc
```

After:
```
403 santri with 403 unique locations:
- Febi Wahyudin: (107.62082, -6.90194)
- dr. Emas Kurniawan: (110.23176, -7.44280)
- drg. Dirja Adriansyah: (110.41302, -7.01888)
- dr. Oni Mulyani: (106.16119, -6.10364)
- Yessi Prakasa, S.H.: (113.72307, -8.18524)
```

## Technical Details

### Haversine Formula
Used to calculate random points within a specified radius:
- Earth radius: 6,371 km
- Random bearing: 0-360°
- Random distance: 0.5-5 km per variation
- Maintains geographic accuracy with proper spherical calculations

### Database Update
```sql
UPDATE santri_pribadi 
SET lokasi = ST_Point(new_lon, new_lat, 4326)
WHERE id = santri_id
```

Uses PostGIS POINT geometry in SRID 4326 (WGS84).

## Verification

To verify current diversification status:

```bash
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) as total, COUNT(DISTINCT ST_AsText(lokasi)) as unique_locs FROM santri_pribadi WHERE lokasi IS NOT NULL'))
    total, unique = result.fetchone()
    print(f'Total: {total}, Unique: {unique}')
"
```

## Analysis Tool

Check duplicate locations:

```bash
python analyze_duplicate_locations.py
```

Shows:
- Distribution of santri by location cluster
- Duplicate count summary
- Location summary

## Notes

- ✅ All coordinates use SRID 4326 (WGS84)
- ✅ Variations are within realistic 2-5 km range
- ✅ No data loss - only geographic coordinates modified
- ✅ Can be reversed if needed (backup coordinates available in git history)
- ✅ Ready for map visualization and geospatial analysis
