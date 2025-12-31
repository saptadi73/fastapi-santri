import requests
import json

url = "http://127.0.0.1:8000/pesantren-fasilitas"
headers = {"Content-Type": "application/json"}

# Test dengan data yang lebih lengkap
data = {
    "pesantren_id": "bfc0e58b-de57-4f22-84e3-5c36cd2002de",
    "jumlah_kamar": 50,
    "jumlah_ruang_kelas": 20,
    "jumlah_masjid": 1,
    "perpustakaan": True,
    "laboratorium": True,
    "ruang_komputer": True,
    "koperasi": True,
    "kantin": True,
    "fasilitas_olahraga": "lapangan_futsal,basket",
    "fasilitas_kesehatan": "klinik",
    "fasilitas_mengajar": "projector,whiteboard",
    "fasilitas_komunikasi": "internet,telepon",
    "akses_transportasi": "angkutan_umum",
    "jarak_ke_kota_km": 5.5,
    "asrama": "layak",
    "ruang_belajar": "cukup",
    "internet": "stabil",
    "fasilitas_transportasi": "bus",
    "akses_jalan": "aspal"
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2))
