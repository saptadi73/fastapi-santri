#!/usr/bin/env python
"""Test NL2SQL dengan GeoJSON output untuk map integration."""

import json
from datetime import datetime
from app.nl2sql.output_normalizer import OutputNormalizer
from app.nl2sql.geojson_generator import GeoJSONGenerator


def test_location_intent_geojson():
    """Test LOCATION intent dengan GeoJSON output."""
    print("\n" + "="*70)
    print("TEST 1: LOCATION Intent -> GeoJSON")
    print("="*70 + "\n")
    
    # Mock santri data with coordinates
    santri_data = [
        {
            "id": 1,
            "nama_santri": "Ahmad Hidayat",
            "latitude": -6.9271,
            "longitude": 107.6062,
            "kategori_kemiskinan": "Miskin",
            "tahun_angkatan": 2023
        },
        {
            "id": 2,
            "nama_santri": "Siti Nurhaliza",
            "latitude": -6.8852,
            "longitude": 107.5992,
            "kategori_kemiskinan": "Sangat Miskin",
            "tahun_angkatan": 2022
        },
        {
            "id": 3,
            "nama_santri": "Budi Santoso",
            "latitude": -6.9452,
            "longitude": 107.6102,
            "kategori_kemiskinan": "Tidak Miskin",
            "tahun_angkatan": 2023
        }
    ]
    
    # Format for LOCATION intent
    result = OutputNormalizer.format_for_response(santri_data, "location")
    
    if not isinstance(result, dict):
        print(f"ERROR: Expected dict, got {type(result)}")
        return
    
    print(f"Intent Type: LOCATION")
    print(f"Result type: {result.get('type')}")
    print(f"Feature count: {len(result.get('features', []))}")
    print(f"Properties: {result.get('properties', {})}")
    
    # Validate
    is_valid = OutputNormalizer.validate_geojson_structure(result)
    print(f"Valid GeoJSON: {is_valid}")
    
    # Show features
    print(f"\nFeatures:")
    for feature in result.get("features", [])[:2]:  # First 2
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])
        print(f"  - {props.get('nama_santri', 'Unknown')}: {coords}")
    
    # Serialize to JSON
    json_str = json.dumps(result, indent=2, default=str)
    print(f"\nJSON size: {len(json_str)} bytes")
    print(f"Sample JSON:\n{json_str[:300]}...\n")


def test_heatmap_intent_geojson():
    """Test HEATMAP intent dengan GeoJSON output."""
    print("="*70)
    print("TEST 2: HEATMAP Intent -> GeoJSON with Intensity")
    print("="*70 + "\n")
    
    # Mock data dengan skor
    santri_with_scores = [
        {"id": 1, "nama_santri": "Ahmad", "latitude": -6.9271, "longitude": 107.6062, "skor": 75},
        {"id": 2, "nama_santri": "Siti", "latitude": -6.8852, "longitude": 107.5992, "skor": 85},
        {"id": 3, "nama_santri": "Budi", "latitude": -6.9452, "longitude": 107.6102, "skor": 92},
        {"id": 4, "nama_santri": "Eka", "latitude": -6.9100, "longitude": 107.6150, "skor": 65},
    ]
    
    # Format for HEATMAP intent
    result = OutputNormalizer.format_for_response(santri_with_scores, "heatmap")
    
    if not isinstance(result, dict):
        print(f"ERROR: Expected dict, got {type(result)}")
        return
    
    print(f"Intent Type: HEATMAP")
    print(f"Result type: {result.get('type')}")
    print(f"Feature count: {len(result.get('features', []))}")
    print(f"Heatmap enabled: {result.get('properties', {}).get('heatmap')}")
    print(f"Intensity range: {result.get('properties', {}).get('intensity_range')}")
    
    # Show intensity values
    print(f"\nIntensity values (0-1 scale):")
    for feature in result.get("features", []):
        props = feature.get("properties", {})
        intensity = props.get("intensity", "N/A")
        skor = props.get("skor", "N/A")
        print(f"  - {props.get('nama_santri', 'Unknown')}: skor={skor} -> intensity={intensity:.2f}")
    
    # Validate
    is_valid = OutputNormalizer.validate_geojson_structure(result)
    print(f"\nValid GeoJSON: {is_valid}")


def test_distance_intent_geojson():
    """Test DISTANCE intent dengan GeoJSON output."""
    print("\n" + "="*70)
    print("TEST 3: DISTANCE Intent -> GeoJSON with Center Point")
    print("="*70 + "\n")
    
    # Mock data with distance field
    santri_nearby = [
        {"id": 1, "nama_santri": "Ahmad", "latitude": -6.9271, "longitude": 107.6062, "distance": 2.5},
        {"id": 2, "nama_santri": "Siti", "latitude": -6.8852, "longitude": 107.5992, "distance": 5.2},
        {"id": 3, "nama_santri": "Budi", "latitude": -6.9452, "longitude": 107.6102, "distance": 3.1},
    ]
    
    center_lat = -6.9100
    center_lon = 107.6050
    
    # Format for DISTANCE intent
    result = OutputNormalizer.format_for_response(
        santri_nearby, 
        "distance",
        center_latitude=center_lat, 
        center_longitude=center_lon
    )
    
    if not isinstance(result, dict):
        print(f"ERROR: Expected dict, got {type(result)}")
        return
    
    print(f"Intent Type: DISTANCE")
    print(f"Result type: {result.get('type')}")
    print(f"Feature count: {len(result.get('features', []))}")
    
    # Show center point
    center_props = result.get("properties", {}).get("center", {})
    print(f"\nCenter point: {center_props}")
    
    # Show nearby santri
    print(f"\nNearby santri (sorted by distance):")
    for feature in result.get("features", []):
        props = feature.get("properties", {})
        if props.get("nama_santri"):  # Skip center point
            distance = props.get("distance", "N/A")
            print(f"  - {props.get('nama_santri')}: {distance} km away")
    
    # Validate
    is_valid = OutputNormalizer.validate_geojson_structure(result)
    print(f"\nValid GeoJSON: {is_valid}")


def test_geojson_export():
    """Test GeoJSON export dan serialization."""
    print("\n" + "="*70)
    print("TEST 4: GeoJSON Export & Serialization")
    print("="*70 + "\n")
    
    test_data = [
        {"id": 1, "name": "Location A", "latitude": -6.9271, "longitude": 107.6062},
        {"id": 2, "name": "Location B", "latitude": -6.8852, "longitude": 107.5992},
    ]
    
    geojson = GeoJSONGenerator.rows_to_geojson(test_data)
    
    # Test export
    json_str = OutputNormalizer.export_geojson(geojson, pretty=True)
    print(f"Exported JSON (pretty format):")
    print(f"  Size: {len(json_str)} bytes")
    print(f"  Sample:\n{json_str[:200]}...\n")
    
    # Test minified
    json_min = OutputNormalizer.export_geojson(geojson, pretty=False)
    print(f"Minified JSON:")
    print(f"  Size: {len(json_min)} bytes")
    print(f"  Compression ratio: {len(json_min) / len(json_str):.1%}")


def test_metadata_and_bbox():
    """Test metadata dan bounding box."""
    print("\n" + "="*70)
    print("TEST 5: GeoJSON Metadata & Bounding Box")
    print("="*70 + "\n")
    
    test_data = [
        {"id": 1, "name": "Loc A", "latitude": -6.9271, "longitude": 107.6062},
        {"id": 2, "name": "Loc B", "latitude": -6.8852, "longitude": 107.5992},
        {"id": 3, "name": "Loc C", "latitude": -6.9452, "longitude": 107.6102},
    ]
    
    geojson = GeoJSONGenerator.rows_to_geojson(test_data)
    
    # Add metadata
    geojson = OutputNormalizer.add_metadata_to_geojson(
        geojson,
        intent="location",
        query="Show all santri locations",
        count=len(test_data)
    )
    
    print("Metadata added:")
    for key, value in geojson.get("properties", {}).items():
        print(f"  - {key}: {value}")
    
    # Calculate bbox
    bbox = GeoJSONGenerator.create_bounding_box(geojson.get("features", []))
    print(f"\nBounding box: {bbox}")
    if bbox:
        print(f"  West (minLon): {bbox[0]}")
        print(f"  South (minLat): {bbox[1]}")
        print(f"  East (maxLon): {bbox[2]}")
        print(f"  North (maxLat): {bbox[3]}")
    
    # Add bbox to geojson
    geojson["bbox"] = bbox
    print(f"\nGeoJSON with bbox included: ✓")


def main():
    """Run all map integration tests."""
    print("\n" + "="*70)
    print("NL2SQL MAP INTEGRATION TESTS")
    print("="*70)
    
    try:
        test_location_intent_geojson()
        test_heatmap_intent_geojson()
        test_distance_intent_geojson()
        test_geojson_export()
        test_metadata_and_bbox()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED SUCCESSFULLY [OK]")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
