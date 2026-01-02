#!/usr/bin/env python
"""Test GeoJSON Generator untuk map integration."""

import json
from app.nl2sql.geojson_generator import GeoJSONGenerator
from app.nl2sql.output_normalizer import OutputNormalizer


def test_geojson_generator():
    """Test GeoJSON generator."""
    print("\n" + "="*70)
    print("TESTING GEOJSON GENERATOR")
    print("="*70 + "\n")
    
    # Test data: Santri locations
    santri_data = [
        {
            "id": "santri-1",
            "nama_santri": "Ahmad Hidayat",
            "kategori_kemiskinan": "Miskin",
            "latitude": -6.9271,
            "longitude": 107.6062,
            "skor": 75
        },
        {
            "id": "santri-2",
            "nama_santri": "Siti Nurhaliza",
            "kategori_kemiskinan": "Sangat Miskin",
            "latitude": -6.8852,
            "longitude": 107.5992,
            "skor": 85
        },
        {
            "id": "santri-3",
            "nama_santri": "Budi Santoso",
            "kategori_kemiskinan": "Miskin",
            "latitude": -6.9452,
            "longitude": 107.6102,
            "skor": 92
        }
    ]
    
    print("1. Testing rows_to_geojson (LOCATION Intent):\n")
    geojson = GeoJSONGenerator.rows_to_geojson(
        rows=santri_data,
        lat_field="latitude",
        lon_field="longitude",
        id_field="id"
    )
    
    print(f"Type: {geojson['type']}")
    print(f"Feature count: {len(geojson['features'])}")
    print(f"Properties: {geojson.get('properties', {})}\n")
    
    # Show first feature
    if geojson["features"]:
        feature = geojson["features"][0]
        print(f"First feature:")
        print(f"  - ID: {feature.get('id')}")
        print(f"  - Geometry type: {feature['geometry']['type']}")
        print(f"  - Coordinates: {feature['geometry']['coordinates']}")
        print(f"  - Properties keys: {list(feature['properties'].keys())}\n")
    
    print("2. Testing rows_to_heatmap_geojson (HEATMAP Intent):\n")
    heatmap_geojson = GeoJSONGenerator.rows_to_heatmap_geojson(
        rows=santri_data,
        lat_field="latitude",
        lon_field="longitude",
        intensity_field="skor",
        intensity_range=(70, 100)
    )
    
    print(f"Heatmap feature count: {len(heatmap_geojson['features'])}")
    print(f"Heatmap properties: {heatmap_geojson.get('properties', {})}\n")
    
    # Show intensity values
    if heatmap_geojson["features"]:
        for feature in heatmap_geojson["features"]:
            intensity = feature["properties"].get("intensity")
            skor = feature["properties"].get("skor", "N/A")
            print(f"  - {feature['properties'].get('nama_santri', 'Unknown')}: skor={skor}, intensity={intensity:.2f}")
    
    print("\n3. Testing rows_to_geojson_with_distance (DISTANCE Intent):\n")
    
    # Add distance field
    distance_data = [
        {**row, "distance": 2.5 + i*0.5}  # Mock distances
        for i, row in enumerate(santri_data)
    ]
    
    distance_geojson = GeoJSONGenerator.rows_to_geojson_with_distance(
        rows=distance_data,
        center_latitude=-6.9000,
        center_longitude=107.6000,
        lat_field="latitude",
        lon_field="longitude",
        distance_field="distance"
    )
    
    print(f"Distance GeoJSON feature count: {len(distance_geojson['features'])}")
    print(f"Has center point: {'center' in distance_geojson.get('properties', {})}")
    print(f"Center coordinates: {distance_geojson['properties'].get('center', {})}\n")
    
    # Show distance sorted
    for i, feature in enumerate(distance_geojson["features"][1:], 1):  # Skip center
        print(f"  {i}. {feature['properties'].get('nama_santri', 'Unknown')}: {feature['properties'].get('distance', 'N/A')} km")
    
    print("\n4. Testing bounding box calculation:\n")
    bbox = GeoJSONGenerator.create_bounding_box(geojson["features"])
    print(f"Bounding box: {bbox}")
    if bbox:
        print(f"  Min Lon: {bbox[0]}, Min Lat: {bbox[1]}")
        print(f"  Max Lon: {bbox[2]}, Max Lat: {bbox[3]}")
    
    print("\n5. Testing with OutputNormalizer integration:\n")
    
    # Test LOCATION intent
    location_output = OutputNormalizer.format_for_response(santri_data, "location")
    if isinstance(location_output, dict):
        print(f"LOCATION intent output type: {location_output.get('type')}")
        print(f"Feature count: {len(location_output.get('features', []))}")
        print(f"Has properties: {'properties' in location_output}")
    else:
        print(f"LOCATION intent output: {type(location_output)}")
    
    # Test HEATMAP intent
    heatmap_output = OutputNormalizer.format_for_response(santri_data, "heatmap")
    if isinstance(heatmap_output, dict):
        print(f"\nHEATMAP intent output type: {heatmap_output.get('type')}")
        print(f"Feature count: {len(heatmap_output.get('features', []))}")
        print(f"Heatmap mode: {heatmap_output.get('properties', {}).get('heatmap')}")
    else:
        print(f"\nHEATMAP intent output: {type(heatmap_output)}")
    
    print("\n6. Verify JSON serializability:\n")
    is_serializable = OutputNormalizer.validate_json_serializable(geojson)
    print(f"GeoJSON serializable to JSON: {is_serializable}")
    
    # Show sample JSON
    if is_serializable:
        json_str = json.dumps(geojson, indent=2, default=str)[:200]
        print(f"\nSample JSON output:\n{json_str}...\n")


if __name__ == "__main__":
    test_geojson_generator()
    print("="*70)
    print("GEOJSON GENERATOR TEST COMPLETED!")
    print("="*70 + "\n")
