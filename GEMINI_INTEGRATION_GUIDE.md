# Gemini AI Integration Guide

## Konfigurasi

Integrasi Gemini AI telah ditambahkan ke sistem. Berikut langkah-langkah setup:

### 1. Dapatkan API Key dari Google AI Studio

1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan akun Google Anda
3. Klik "Create API Key"
4. Copy API key yang dihasilkan

### 2. Update File .env

Edit file `.env` dan ganti placeholder dengan API key Anda:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3. Install Dependencies

Jalankan perintah berikut untuk install dependencies baru:

```bash
pip uninstall google-generativeai -y
pip install -r requirements.txt
```

**Catatan:** Package `google-generativeai` sudah deprecated, kita menggunakan `google-genai` yang baru.

### 4. Restart Aplikasi

Restart aplikasi FastAPI agar konfigurasi diterapkan.

## Endpoints yang Tersedia

### 1. Analisis Gambar Tunggal
**POST** `/gemini/analyze/image`

Menganalisis gambar tunggal dengan prompt kustom (opsional).

**Parameters:**
- `file`: File gambar (JPG, PNG, GIF, WEBP, BMP)
- `prompt`: Prompt analisis kustom (opsional)

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/analyze/image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg" \
  -F "prompt=Jelaskan kondisi bangunan ini"
```

### 2. Analisis Video
**POST** `/gemini/analyze/video`

Menganalisis video (max 20MB).

**Parameters:**
- `file`: File video (MP4, MOV, AVI, WEBM)
- `prompt`: Prompt analisis kustom (opsional)

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/analyze/video" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/video.mp4" \
  -F "prompt=Apa yang terjadi dalam video ini?"
```

### 3. Analisis Multiple Gambar
**POST** `/gemini/analyze/multiple-images`

Menganalisis beberapa gambar sekaligus (max 10 gambar).

**Parameters:**
- `files`: Array file gambar
- `prompt`: Prompt analisis kustom (opsional)

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/analyze/multiple-images" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.jpg" \
  -F "files=@/path/to/image3.jpg" \
  -F "prompt=Bandingkan kondisi ketiga fasilitas ini"
```

### 4. OCR (Extract Text)
**POST** `/gemini/ocr`

Ekstrak teks dari gambar.

**Parameters:**
- `file`: File gambar yang mengandung teks

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/ocr" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.jpg"
```

### 5. Analisis Fasilitas Pesantren
**POST** `/gemini/analyze/pesantren-facility`

Analisis khusus untuk fasilitas pesantren dengan template penilaian standar.

**Parameters:**
- `file`: Gambar fasilitas pesantren

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/analyze/pesantren-facility" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/facility.jpg"
```

### 6. Analisis Rumah Santri
**POST** `/gemini/analyze/santri-housing`

Analisis khusus untuk kondisi rumah santri dengan fokus indikator sosio-ekonomi.

**Parameters:**
- `file`: Gambar rumah santri

**Contoh curl:**
```bash
curl -X POST "http://localhost:8000/gemini/analyze/santri-housing" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/house.jpg"
```

### 7. Health Check
**GET** `/gemini/health`

Cek status konfigurasi Gemini AI.

**Contoh curl:**
```bash
curl -X GET "http://localhost:8000/gemini/health"
```

## Contoh Penggunaan dengan Python

```python
import requests

# Setup
API_URL = "http://localhost:8000"
TOKEN = "your-auth-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Analisis gambar
with open("facility.jpg", "rb") as f:
    files = {"file": f}
    data = {"prompt": "Jelaskan kondisi fasilitas ini"}
    response = requests.post(
        f"{API_URL}/gemini/analyze/image",
        headers=headers,
        files=files,
        data=data
    )
    print(response.json())

# Analisis video
with open("inspection.mp4", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{API_URL}/gemini/analyze/video",
        headers=headers,
        files=files
    )
    print(response.json())

# Multiple images
with open("img1.jpg", "rb") as f1, \
     open("img2.jpg", "rb") as f2:
    files = [
        ("files", f1),
        ("files", f2)
    ]
    response = requests.post(
        f"{API_URL}/gemini/analyze/multiple-images",
        headers=headers,
        files=files
    )
    print(response.json())
```

## Model yang Digunakan

Default model: `gemini-1.5-flash`
- Cepat dan efisien
- Mendukung gambar dan video
- Multimodal (teks + vision)

Untuk menggunakan model lain, edit di `.env`:
```env
GEMINI_MODEL=gemini-1.5-pro  # Model lebih canggih tapi lebih lambat
```

## Batasan & Tips

### Batasan:
- Video maksimal 20MB (tier gratis)
- Multiple images maksimal 10 gambar per request
- Rate limit sesuai dengan quota API key Anda

### Tips:
- Gambar akan otomatis di-resize jika terlalu besar
- Gunakan prompt yang spesifik untuk hasil lebih baik
- Endpoint khusus (pesantren-facility, santri-housing) sudah punya template prompt yang optimal
- OCR endpoint cocok untuk ekstrak teks dari dokumen/sertifikat

## Troubleshooting

### Error: "GEMINI_API_KEY not configured"
- Pastikan API key sudah diisi di file `.env`
- Restart aplikasi setelah update `.env`

### Error: "Invalid file type"
- Cek format file yang di-upload
- Gambar: JPG, PNG, GIF, WEBP, BMP
- Video: MP4, MOV, AVI, WEBM

### Error: "Video file too large"
- Kompres video atau gunakan resolusi lebih rendah
- Maksimal 20MB untuk tier gratis

### Hasil analisis kurang akurat
- Gunakan prompt yang lebih spesifik
- Upload gambar dengan kualitas lebih baik
- Pastikan objek yang ingin dianalisis terlihat jelas

## Dokumentasi Interaktif

Setelah aplikasi berjalan, akses Swagger UI di:
```
http://localhost:8000/docs
```

Semua endpoint Gemini AI ada di section "Gemini AI Vision".
