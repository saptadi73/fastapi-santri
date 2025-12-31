# Quick Start - GIS Integration

## Status: Ready to Use

Both GIS mapping systems are **fully separated and functional**:

### Santri Map

- Endpoint: `/santri-map/*`
- Data: 1 santri (Aji Pangestu - Tidak Miskin)
- Auto-update: Enabled when santri scoring is calculated

### Pesantren Map

- Endpoint: `/pesantren-map/*`
- Data: 1 pesantren (Mahasina - Sangat Layak)
- Auto-update: Enabled when pesantren scoring is calculated

---

## Test API Now

### Santri Map

**Statistics:**

```bash
curl http://127.0.0.1:8000/santri-map/statistics
```

**GeoJSON:**

```bash
curl http://127.0.0.1:8000/santri-map/geojson?limit=10
```

### Pesantren Map

**Statistics:**

```bash
curl http://127.0.0.1:8000/pesantren-map/statistics
```

**GeoJSON:**

```bash
curl http://127.0.0.1:8000/pesantren-map/geojson?limit=10
```

---

## Open Demo Page

**File:** `INTEGRATION_GIS_EXAMPLE.html`

**Features:**

- Toggle between Santri / Pesantren / Both layers
- Filter by kategori, provinsi, kabupaten
- Interactive popups
- Real-time statistics
- Color-coded markers

**How to open:**

1. Open `INTEGRATION_GIS_EXAMPLE.html` in browser
2. Select layer (Santri/Pesantren/Both)
3. Apply filter and click "Tampilkan"
4. Click marker for details

---

## Documentation

1. **API Documentation**: `app/docs/API_DOCUMENTATION.md` (lines 2990-3300)
2. **Integration Guide**: `GIS_INTEGRATION_GUIDE.md`
3. **Test Summary**: `TEST_PESANTREN_MAP_SUMMARY.md`

---

## Color Scheme

### Santri (Circle Markers)

- Sangat Miskin: `#d32f2f` (Red)
- Miskin: `#f57c00` (Orange)
- Rentan: `#fbc02d` (Yellow)
- Tidak Miskin: `#388e3c` (Green)

### Pesantren (Pin Markers)

- Sangat Layak: `#1b5e20` (Dark Green)
- Layak: `#4caf50` (Light Green)
- Cukup Layak: `#fbc02d` (Yellow)
- Tidak Layak: `#d32f2f` (Red)

---

## Verified Features

| Feature | Santri | Pesantren |
|---------|--------|-----------|
| GeoJSON endpoint | ✅ | ✅ |
| Bounding box query | ✅ | ✅ |
| Statistics API | ✅ | ✅ |
| Filter by category | ✅ | ✅ |
| Auto-update on scoring | ✅ | ✅ |
| Data in database | ✅ | ✅ |

---

## Frontend Integration Examples

### Leaflet (Simple)

```javascript
const map = L.map('map').setView([-7.5, 108.2], 9);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

fetch('http://127.0.0.1:8000/santri-map/geojson?limit=500')
  .then(res => res.json())
  .then(geojson => {
    L.geoJSON(geojson).addTo(map);
  });
```

### React + react-leaflet

```jsx
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

function MyMap() {
  const [data, setData] = React.useState(null);

  React.useEffect(() => {
    fetch('http://127.0.0.1:8000/santri-map/geojson')
      .then(r => r.json())
      .then(setData);
  }, []);

  return (
    <MapContainer center={[-7.5, 108.2]} zoom={9} style={{height: '600px'}}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {data && <GeoJSON data={data} />}
    </MapContainer>
  );
}
```

---

## Next Steps

1. Open `INTEGRATION_GIS_EXAMPLE.html` in browser
2. Test endpoints with provided curl commands
3. Integrate into your frontend using examples above
4. See `GIS_INTEGRATION_GUIDE.md` for detailed implementation

**Happy mapping!**
