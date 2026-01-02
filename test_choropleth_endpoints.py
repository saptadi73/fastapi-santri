"""
Test script untuk Choropleth Map endpoints
Pastikan server sudah running di http://localhost:8000
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def test_choropleth_stats():
    """Test endpoint statistik choropleth"""
    print_header("Test: GET /gis/choropleth/stats")
    
    try:
        response = requests.get(f"{BASE_URL}/gis/choropleth/stats")
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✅ Success! Status Code:", response.status_code)
        print("\nSantri Categories:")
        for cat in data.get('santri_categories', [])[:5]:
            print(f"  - {cat['kategori']}: {cat['count']} santri")
        
        print("\nPesantren Categories:")
        for cat in data.get('pesantren_categories', [])[:5]:
            print(f"  - {cat['kategori']}: {cat['count']} pesantren")
        
        print(f"\nTotal Provinsi: {len(data.get('provinsi_list', []))}")
        print(f"Total Kabupaten: {len(data.get('kabupaten_list', []))}")
        
        if data.get('provinsi_list'):
            print(f"Provinsi pertama: {data['provinsi_list'][0]}")
        if data.get('kabupaten_list'):
            print(f"Kabupaten pertama: {data['kabupaten_list'][0]}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return False

def test_santri_choropleth(provinsi=None, kategori=None):
    """Test endpoint choropleth santri"""
    print_header("Test: GET /gis/choropleth/santri-kabupaten")
    
    params = {}
    if provinsi:
        params['provinsi'] = provinsi
    if kategori:
        params['kategori_kemiskinan'] = kategori
    
    print(f"\nParameters: {params if params else 'None (all data)'}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/gis/choropleth/santri-kabupaten",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✅ Success! Status Code:", response.status_code)
        print(f"Type: {data.get('type')}")
        print(f"Total Features (Kabupaten): {len(data.get('features', []))}")
        
        # Show first 3 kabupaten
        for i, feature in enumerate(data.get('features', [])[:3], 1):
            props = feature['properties']
            print(f"\n{i}. Kabupaten: {props['kabupaten']}, {props['provinsi']}")
            print(f"   Total Santri: {props['total_santri']}")
            print(f"   Sangat Miskin: {props['sangat_miskin']} ({props['pct_sangat_miskin']}%)")
            print(f"   Miskin: {props['miskin']} ({props['pct_miskin']}%)")
            print(f"   Rentan: {props['rentan']}")
            print(f"   Tidak Miskin: {props['tidak_miskin']}")
            print(f"   Avg Score: {props['avg_skor']}")
        
        # Calculate totals
        if data.get('features'):
            total_santri = sum(f['properties']['total_santri'] for f in data['features'])
            total_sangat_miskin = sum(f['properties']['sangat_miskin'] for f in data['features'])
            total_miskin = sum(f['properties']['miskin'] for f in data['features'])
            
            print(f"\nSummary:")
            print(f"  Total Santri across all kabupaten: {total_santri}")
            print(f"  Total Sangat Miskin: {total_sangat_miskin}")
            print(f"  Total Miskin: {total_miskin}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def test_pesantren_choropleth(provinsi=None, kategori=None):
    """Test endpoint choropleth pesantren"""
    print_header("Test: GET /gis/choropleth/pesantren-kabupaten")
    
    params = {}
    if provinsi:
        params['provinsi'] = provinsi
    if kategori:
        params['kategori_kelayakan'] = kategori
    
    print(f"\nParameters: {params if params else 'None (all data)'}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/gis/choropleth/pesantren-kabupaten",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✅ Success! Status Code:", response.status_code)
        print(f"Type: {data.get('type')}")
        print(f"Total Features (Kabupaten): {len(data.get('features', []))}")
        
        # Show first 3 kabupaten
        for i, feature in enumerate(data.get('features', [])[:3], 1):
            props = feature['properties']
            print(f"\n{i}. Kabupaten: {props['kabupaten']}, {props['provinsi']}")
            print(f"   Total Pesantren: {props['total_pesantren']}")
            print(f"   Sangat Layak: {props['sangat_layak']} ({props['pct_sangat_layak']}%)")
            print(f"   Layak: {props['layak']} ({props['pct_layak']}%)")
            print(f"   Cukup Layak: {props['cukup_layak']}")
            print(f"   Kurang Layak: {props['kurang_layak']}")
            print(f"   Avg Score: {props['avg_skor']}")
            print(f"   Total Santri: {props['total_santri_pesantren']}")
        
        # Calculate totals
        if data.get('features'):
            total_pesantren = sum(f['properties']['total_pesantren'] for f in data['features'])
            total_santri = sum(f['properties']['total_santri_pesantren'] for f in data['features'])
            
            print(f"\nSummary:")
            print(f"  Total Pesantren across all kabupaten: {total_pesantren}")
            print(f"  Total Santri in pesantren: {total_santri}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def test_geojson_structure():
    """Test struktur GeoJSON response"""
    print_header("Test: GeoJSON Structure Validation")
    
    try:
        response = requests.get(f"{BASE_URL}/gis/choropleth/santri-kabupaten")
        response.raise_for_status()
        
        data = response.json()
        
        # Validate GeoJSON structure
        checks = {
            "Has 'type' field": 'type' in data,
            "Type is 'FeatureCollection'": data.get('type') == 'FeatureCollection',
            "Has 'features' array": 'features' in data and isinstance(data['features'], list),
        }
        
        if data.get('features'):
            first_feature = data['features'][0]
            checks.update({
                "Feature has 'type'": 'type' in first_feature,
                "Feature type is 'Feature'": first_feature.get('type') == 'Feature',
                "Feature has 'geometry'": 'geometry' in first_feature,
                "Feature has 'properties'": 'properties' in first_feature,
                "Geometry has 'type'": 'type' in first_feature.get('geometry', {}),
                "Geometry has 'coordinates'": 'coordinates' in first_feature.get('geometry', {}),
            })
            
            props = first_feature.get('properties', {})
            required_props = [
                'kabupaten', 'provinsi', 'total_santri', 
                'sangat_miskin', 'miskin', 'rentan', 'tidak_miskin',
                'avg_skor', 'pct_sangat_miskin', 'pct_miskin'
            ]
            
            for prop in required_props:
                checks[f"Has property '{prop}'"] = prop in props
        
        print("\nGeoJSON Validation Results:")
        all_pass = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
            if not result:
                all_pass = False
        
        if all_pass:
            print("\n✅ All validations passed! GeoJSON structure is correct.")
        else:
            print("\n⚠️ Some validations failed. Check structure above.")
        
        return all_pass
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    print("\n" + "=" * 80)
    print("  CHOROPLETH MAP ENDPOINTS TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    results = []
    
    # Test 1: Statistics
    results.append(("Statistics", test_choropleth_stats()))
    
    # Test 2: Santri choropleth (all data)
    results.append(("Santri Choropleth (All)", test_santri_choropleth()))
    
    # Test 3: Santri choropleth (filtered by province)
    # Uncomment and adjust province name if needed
    # results.append(("Santri Choropleth (Jawa Barat)", 
    #                 test_santri_choropleth(provinsi="Jawa Barat")))
    
    # Test 4: Pesantren choropleth (all data)
    results.append(("Pesantren Choropleth (All)", test_pesantren_choropleth()))
    
    # Test 5: GeoJSON structure validation
    results.append(("GeoJSON Structure", test_geojson_structure()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
