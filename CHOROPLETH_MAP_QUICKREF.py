"""
Choropleth Map Quick Reference

Endpoint baru untuk visualisasi peta choropleth tingkat kabupaten:
1. /gis/choropleth/santri-kabupaten - Agregasi santri per kabupaten
2. /gis/choropleth/pesantren-kabupaten - Agregasi pesantren per kabupaten
3. /gis/choropleth/stats - Statistik untuk filter dan legend

===============================================================================
SANTRI CHOROPLETH - Contoh Response
===============================================================================
"""

import requests
import json

# Get santri choropleth data
response = requests.get('http://localhost:8000/gis/choropleth/santri-kabupaten')
data = response.json()

print("=" * 80)
print("SANTRI CHOROPLETH DATA")
print("=" * 80)

for feature in data['features'][:2]:  # Show first 2 kabupaten
    props = feature['properties']
    print(f"\nKabupaten: {props['kabupaten']}, {props['provinsi']}")
    print(f"  Total Santri: {props['total_santri']}")
    print(f"  Sangat Miskin: {props['sangat_miskin']} ({props['pct_sangat_miskin']}%)")
    print(f"  Miskin: {props['miskin']} ({props['pct_miskin']}%)")
    print(f"  Rentan: {props['rentan']}")
    print(f"  Tidak Miskin: {props['tidak_miskin']}")
    print(f"  Avg Score: {props['avg_skor']}")

"""
===============================================================================
PESANTREN CHOROPLETH - Contoh Response
===============================================================================
"""

response = requests.get('http://localhost:8000/gis/choropleth/pesantren-kabupaten')
data = response.json()

print("\n" + "=" * 80)
print("PESANTREN CHOROPLETH DATA")
print("=" * 80)

for feature in data['features'][:2]:  # Show first 2 kabupaten
    props = feature['properties']
    print(f"\nKabupaten: {props['kabupaten']}, {props['provinsi']}")
    print(f"  Total Pesantren: {props['total_pesantren']}")
    print(f"  Sangat Layak: {props['sangat_layak']} ({props['pct_sangat_layak']}%)")
    print(f"  Layak: {props['layak']} ({props['pct_layak']}%)")
    print(f"  Cukup Layak: {props['cukup_layak']}")
    print(f"  Kurang Layak: {props['kurang_layak']}")
    print(f"  Avg Score: {props['avg_skor']}")
    print(f"  Total Santri: {props['total_santri_pesantren']}")

"""
===============================================================================
FRONTEND INTEGRATION - Leaflet.js Example
===============================================================================
"""

leaflet_example = '''
// 1. Load Choropleth Data
async function loadSantriChoropleth() {
  const response = await fetch('/gis/choropleth/santri-kabupaten');
  const geojson = await response.json();
  
  // 2. Add to map with color scale
  L.geoJSON(geojson, {
    style: function(feature) {
      const score = feature.properties.avg_skor;
      return {
        fillColor: getColorByScore(score),
        weight: 1,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7
      };
    },
    onEachFeature: function(feature, layer) {
      const props = feature.properties;
      
      // Popup with details
      layer.bindPopup(`
        <div class="choropleth-popup">
          <h3>${props.kabupaten}</h3>
          <p>${props.provinsi}</p>
          <hr>
          <table>
            <tr><td>Total Santri:</td><td><b>${props.total_santri}</b></td></tr>
            <tr><td>Sangat Miskin:</td><td>${props.sangat_miskin} (${props.pct_sangat_miskin}%)</td></tr>
            <tr><td>Miskin:</td><td>${props.miskin} (${props.pct_miskin}%)</td></tr>
            <tr><td>Rentan:</td><td>${props.rentan}</td></tr>
            <tr><td>Tidak Miskin:</td><td>${props.tidak_miskin}</td></tr>
            <tr><td>Avg Score:</td><td><b>${props.avg_skor}</b></td></tr>
          </table>
        </div>
      `);
      
      // Hover effect
      layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight
      });
    }
  }).addTo(map);
  
  // 3. Add legend
  addLegend();
}

// Color scale function
function getColorByScore(score) {
  return score >= 80 ? '#d73027' :  // Sangat Miskin (dark red)
         score >= 65 ? '#fc8d59' :  // Miskin (orange)
         score >= 45 ? '#fee08b' :  // Rentan (yellow)
                       '#91cf60';   // Tidak Miskin (green)
}

function highlightFeature(e) {
  const layer = e.target;
  layer.setStyle({
    weight: 3,
    color: '#666',
    fillOpacity: 0.9
  });
  layer.bringToFront();
}

function resetHighlight(e) {
  geojsonLayer.resetStyle(e.target);
}

// Add legend control
function addLegend() {
  const legend = L.control({position: 'bottomright'});
  
  legend.onAdd = function(map) {
    const div = L.DomUtil.create('div', 'info legend');
    const grades = [0, 45, 65, 80];
    const labels = ['Tidak Miskin', 'Rentan', 'Miskin', 'Sangat Miskin'];
    
    div.innerHTML = '<h4>Kategori Kemiskinan</h4>';
    
    for (let i = 0; i < grades.length; i++) {
      div.innerHTML +=
        '<i style="background:' + getColorByScore(grades[i] + 1) + '"></i> ' +
        labels[i] + '<br>';
    }
    
    return div;
  };
  
  legend.addTo(map);
}
'''

print("\n" + "=" * 80)
print("LEAFLET.JS INTEGRATION")
print("=" * 80)
print(leaflet_example)

"""
===============================================================================
FRONTEND INTEGRATION - Vue.js + Leaflet Example
===============================================================================
"""

vue_example = '''
<template>
  <div class="choropleth-map">
    <div class="map-controls">
      <select v-model="selectedProvinsi" @change="loadData">
        <option value="">Semua Provinsi</option>
        <option v-for="prov in provinsiList" :key="prov" :value="prov">
          {{ prov }}
        </option>
      </select>
      
      <select v-model="selectedKategori" @change="loadData">
        <option value="">Semua Kategori</option>
        <option v-for="cat in categories" :key="cat.kategori" :value="cat.kategori">
          {{ cat.kategori }} ({{ cat.count }})
        </option>
      </select>
      
      <button @click="toggleLayer">
        {{ showSantri ? 'Tampilkan Pesantren' : 'Tampilkan Santri' }}
      </button>
    </div>
    
    <div ref="mapContainer" class="map-container"></div>
    
    <div class="map-stats">
      <h3>Statistik</h3>
      <p>Total Kabupaten: {{ totalKabupaten }}</p>
      <p v-if="showSantri">Total Santri: {{ totalSantri }}</p>
      <p v-else>Total Pesantren: {{ totalPesantren }}</p>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export default {
  name: 'ChoroplethMap',
  data() {
    return {
      map: null,
      geojsonLayer: null,
      showSantri: true,
      selectedProvinsi: '',
      selectedKategori: '',
      provinsiList: [],
      categories: [],
      totalKabupaten: 0,
      totalSantri: 0,
      totalPesantren: 0
    };
  },
  async mounted() {
    this.initMap();
    await this.loadStats();
    await this.loadData();
  },
  methods: {
    initMap() {
      this.map = L.map(this.$refs.mapContainer).setView([-6.9, 107.6], 8);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map);
    },
    
    async loadStats() {
      const response = await fetch('/gis/choropleth/stats');
      const data = await response.json();
      
      this.provinsiList = data.provinsi_list;
      this.categories = this.showSantri ? 
        data.santri_categories : 
        data.pesantren_categories;
    },
    
    async loadData() {
      // Remove existing layer
      if (this.geojsonLayer) {
        this.map.removeLayer(this.geojsonLayer);
      }
      
      // Build URL with filters
      const endpoint = this.showSantri ? 
        '/gis/choropleth/santri-kabupaten' : 
        '/gis/choropleth/pesantren-kabupaten';
      
      const params = new URLSearchParams();
      if (this.selectedProvinsi) params.append('provinsi', this.selectedProvinsi);
      if (this.selectedKategori) {
        const paramName = this.showSantri ? 'kategori_kemiskinan' : 'kategori_kelayakan';
        params.append(paramName, this.selectedKategori);
      }
      
      const url = `${endpoint}?${params.toString()}`;
      const response = await fetch(url);
      const geojson = await response.json();
      
      // Calculate stats
      this.totalKabupaten = geojson.features.length;
      if (this.showSantri) {
        this.totalSantri = geojson.features.reduce(
          (sum, f) => sum + f.properties.total_santri, 0
        );
      } else {
        this.totalPesantren = geojson.features.reduce(
          (sum, f) => sum + f.properties.total_pesantren, 0
        );
      }
      
      // Add to map
      this.geojsonLayer = L.geoJSON(geojson, {
        style: this.getStyle,
        onEachFeature: this.onEachFeature
      }).addTo(this.map);
      
      // Fit bounds
      if (geojson.features.length > 0) {
        this.map.fitBounds(this.geojsonLayer.getBounds());
      }
    },
    
    getStyle(feature) {
      const score = feature.properties.avg_skor;
      return {
        fillColor: this.getColor(score),
        weight: 1,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7
      };
    },
    
    getColor(score) {
      return score >= 80 ? '#d73027' :
             score >= 65 ? '#fc8d59' :
             score >= 45 ? '#fee08b' :
                           '#91cf60';
    },
    
    onEachFeature(feature, layer) {
      const props = feature.properties;
      
      let popupContent = `
        <div class="popup">
          <h3>${props.kabupaten}</h3>
          <p>${props.provinsi}</p>
          <hr>
      `;
      
      if (this.showSantri) {
        popupContent += `
          <p><b>Total Santri:</b> ${props.total_santri}</p>
          <p>Sangat Miskin: ${props.sangat_miskin} (${props.pct_sangat_miskin}%)</p>
          <p>Miskin: ${props.miskin} (${props.pct_miskin}%)</p>
          <p>Rentan: ${props.rentan}</p>
          <p>Tidak Miskin: ${props.tidak_miskin}</p>
          <p><b>Avg Score:</b> ${props.avg_skor}</p>
        `;
      } else {
        popupContent += `
          <p><b>Total Pesantren:</b> ${props.total_pesantren}</p>
          <p>Sangat Layak: ${props.sangat_layak} (${props.pct_sangat_layak}%)</p>
          <p>Layak: ${props.layak} (${props.pct_layak}%)</p>
          <p>Cukup Layak: ${props.cukup_layak}</p>
          <p>Kurang Layak: ${props.kurang_layak}</p>
          <p><b>Avg Score:</b> ${props.avg_skor}</p>
          <p><b>Total Santri:</b> ${props.total_santri_pesantren}</p>
        `;
      }
      
      popupContent += '</div>';
      layer.bindPopup(popupContent);
      
      // Hover effects
      layer.on({
        mouseover: (e) => {
          e.target.setStyle({ weight: 3, fillOpacity: 0.9 });
        },
        mouseout: (e) => {
          this.geojsonLayer.resetStyle(e.target);
        }
      });
    },
    
    async toggleLayer() {
      this.showSantri = !this.showSantri;
      this.selectedKategori = '';
      await this.loadStats();
      await this.loadData();
    }
  }
};
</script>

<style scoped>
.choropleth-map {
  position: relative;
  width: 100%;
  height: 100vh;
}

.map-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.map-controls select,
.map-controls button {
  margin: 5px;
  padding: 5px 10px;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-stats {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 1000;
  background: white;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>
'''

print("\n" + "=" * 80)
print("VUE.JS INTEGRATION")
print("=" * 80)
print(vue_example)

"""
===============================================================================
FILTER EXAMPLES
===============================================================================
"""

print("\n" + "=" * 80)
print("FILTER EXAMPLES")
print("=" * 80)

examples = {
    "All santri in Jawa Barat": "/gis/choropleth/santri-kabupaten?provinsi=Jawa%20Barat",
    "Only 'Miskin' category santri": "/gis/choropleth/santri-kabupaten?kategori_kemiskinan=Miskin",
    "Miskin santri in Jawa Barat": "/gis/choropleth/santri-kabupaten?provinsi=Jawa%20Barat&kategori_kemiskinan=Miskin",
    "All pesantren in Jawa Timur": "/gis/choropleth/pesantren-kabupaten?provinsi=Jawa%20Timur",
    "Only 'Layak' pesantren": "/gis/choropleth/pesantren-kabupaten?kategori_kelayakan=Layak",
    "Get statistics for filters": "/gis/choropleth/stats"
}

for desc, url in examples.items():
    print(f"\n{desc}:")
    print(f"  {url}")

print("\n" + "=" * 80)
print("COLOR SCHEMES")
print("=" * 80)

color_schemes = """
SANTRI (Poverty Level):
  Sangat Miskin (80-100): #d73027 (Dark Red)
  Miskin (65-79):         #fc8d59 (Orange)
  Rentan (45-64):         #fee08b (Yellow)
  Tidak Miskin (0-44):    #91cf60 (Green)

PESANTREN (Eligibility Level):
  Sangat Layak (80-100):  #1a9850 (Dark Green)
  Layak (65-79):          #91cf60 (Light Green)
  Cukup Layak (45-64):    #fee08b (Yellow)
  Kurang Layak (0-44):    #fc8d59 (Orange)

Alternative color schemes dapat menggunakan:
- ColorBrewer (http://colorbrewer2.org/)
- Viridis, Plasma, Inferno palettes
"""

print(color_schemes)

print("\n" + "=" * 80)
print("NOTES")
print("=" * 80)

notes = """
1. Response adalah GeoJSON FeatureCollection standard
2. Geometry menggunakan data dari tabel kabupaten (boundary polygons)
3. Properties berisi agregasi data santri/pesantren
4. Filter bersifat optional - tanpa filter akan return semua kabupaten
5. Data di-cache dapat diimplementasi di frontend untuk performa
6. Untuk province/district boundaries, pastikan tabel kabupaten sudah ada
7. ST_Contains digunakan untuk spatial join dengan kabupaten boundaries
"""

print(notes)
