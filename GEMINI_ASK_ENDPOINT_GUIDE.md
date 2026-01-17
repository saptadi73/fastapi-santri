# Dokumentasi Endpoint Gemini Ask Question

## Gambaran Umum

Endpoint `/gemini/ask` memungkinkan pengguna untuk mengajukan pertanyaan kepada AI Assistant yang khusus dirancang untuk aplikasi **Program Bantuan Santri**. Endpoint ini menggunakan Google Gemini AI dengan system instruction yang telah dikonfigurasi untuk membatasi topik pembahasan.

## Endpoint Details

- **URL**: `/gemini/ask`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Authentication**: Tidak memerlukan autentikasi (sesuai dengan konfigurasi aplikasi)

## Request Format

```json
{
  "question": "string (5-1000 karakter)"
}
```

### Parameter

| Parameter | Type | Required | Validasi | Deskripsi |
|-----------|------|----------|----------|-----------|
| question | string | Ya | min: 5, max: 1000 karakter | Pertanyaan yang ingin diajukan kepada asisten |

## Response Format

### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "Pertanyaan yang diajukan",
    "answer": "Jawaban dari AI assistant",
    "model": "gemini-2.0-flash-exp"
  }
}
```

### Error Response (422 Validation Error)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "question"],
      "msg": "String should have at least 5 characters",
      "input": "abc",
      "ctx": {
        "min_length": 5
      }
    }
  ]
}
```

### Error Response (500 Internal Server Error)

```json
{
  "detail": "Failed to process question: [error message]"
}
```

## Topik yang Diperbolehkan

Asisten dapat menjawab pertanyaan seputar topik berikut:

1. **Santri dan Kehidupan Santri**
   - Kehidupan sehari-hari santri
   - Sistem pembelajaran santri
   - Hak dan kewajiban santri

2. **Pesantren**
   - Sejarah pesantren
   - Sistem pendidikan pesantren
   - Kurikulum dan metode pembelajaran
   - Jenis-jenis pesantren

3. **Nahdlatul Ulama (NU)**
   - Sejarah NU
   - Peran NU dalam pendidikan
   - Organisasi dan struktur NU

4. **Program Bantuan Sosial**
   - Jenis-jenis bantuan sosial
   - Mekanisme penyaluran bantuan
   - Kriteria penerima bantuan
   - Prosedur pendaftaran

5. **Pengentasan Kemiskinan**
   - Program pengentasan kemiskinan
   - Strategi penanggulangan kemiskinan
   - Peran pesantren dalam pengentasan kemiskinan

6. **Pendidikan**
   - Pendidikan formal dan non-formal
   - Sistem pendidikan pesantren
   - Kurikulum dan metode pembelajaran

7. **Dakwah**
   - Metode dakwah
   - Sejarah dakwah di Indonesia
   - Peran pesantren dalam dakwah

8. **Kitab Kuning**
   - Pengertian kitab kuning
   - Jenis-jenis kitab kuning
   - Metode pembelajaran kitab kuning

9. **Islam**
   - Ajaran Islam
   - Praktik ibadah
   - Akhlak dan muamalah
   - Fiqh dan ushul fiqh

10. **Sejarah Islam**
    - Sejarah Islam di Indonesia
    - Perkembangan Islam
    - Tokoh-tokoh Islam

11. **Sejarah Pesantren**
    - Perkembangan pesantren di Indonesia
    - Pesantren-pesantren bersejarah
    - Tokoh-tokoh pesantren

12. **Hari Santri**
    - Sejarah Hari Santri (22 Oktober)
    - Makna dan filosofi Hari Santri
    - Peringatan Hari Santri

13. **Hari Pahlawan**
    - Sejarah Hari Pahlawan
    - Pahlawan nasional
    - Nilai-nilai kepahlawanan

## Topik yang Dilarang

Asisten **TIDAK AKAN** menjawab pertanyaan tentang:

1. **Politik Praktis**
   - Kebijakan pemerintah yang kontroversial
   - Isu politik terkini
   - Kampanye politik

2. **Partai Politik**
   - Perbandingan partai politik
   - Ideologi partai politik
   - Kampanye partai

3. **Perbandingan Agama**
   - Debat antar agama
   - Perbandingan ajaran agama
   - Konten yang dapat memecah belah

## Contoh Penggunaan

### Contoh 1: Pertanyaan Valid tentang Pesantren

**Request:**
```bash
curl -X POST "http://localhost:8000/gemini/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Apa itu pesantren dan bagaimana sistem pendidikannya?"
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "Apa itu pesantren dan bagaimana sistem pendidikannya?",
    "answer": "Pesantren adalah lembaga pendidikan Islam tradisional di Indonesia yang fokus pada pengajaran ilmu-ilmu agama Islam. Sistem pendidikannya meliputi:\n\n1. **Pembelajaran Kitab Kuning**: Santri mempelajari kitab-kitab klasik Islam dalam bahasa Arab\n2. **Sistem Sorogan**: Pembelajaran individual antara santri dan kyai\n3. **Sistem Bandongan**: Pembelajaran kelompok di mana kyai membacakan dan menjelaskan kitab\n4. **Kehidupan Berasrama**: Santri tinggal di pondok pesantren dan belajar tidak hanya ilmu agama tetapi juga nilai-nilai kehidupan\n\nPesantren memadukan pendidikan formal dan non-formal untuk membentuk karakter santri yang berakhlak mulia.",
    "model": "gemini-2.0-flash-exp"
  }
}
```

### Contoh 2: Pertanyaan Valid tentang Hari Santri

**Request:**
```bash
curl -X POST "http://localhost:8000/gemini/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bagaimana sejarah Hari Santri di Indonesia?"
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "Bagaimana sejarah Hari Santri di Indonesia?",
    "answer": "Hari Santri diperingati setiap tanggal 22 Oktober untuk mengenang Resolusi Jihad yang dikeluarkan oleh KH. Hasyim Asy'ari pada 22 Oktober 1945...",
    "model": "gemini-2.0-flash-exp"
  }
}
```

### Contoh 3: Pertanyaan Tentang Politik (Akan Ditolak)

**Request:**
```bash
curl -X POST "http://localhost:8000/gemini/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Apa pendapat Anda tentang partai politik di Indonesia?"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "Apa pendapat Anda tentang partai politik di Indonesia?",
    "answer": "Maaf, saya tidak dapat membahas topik partai politik karena di luar ruang lingkup asisten Program Bantuan Santri. Silakan ajukan pertanyaan seputar santri, pesantren, pendidikan, atau bantuan sosial.",
    "model": "gemini-2.0-flash-exp"
  }
}
```

### Contoh 4: Pertanyaan Di Luar Topik

**Request:**
```bash
curl -X POST "http://localhost:8000/gemini/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bagaimana cara membuat kue brownies?"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "Bagaimana cara membuat kue brownies?",
    "answer": "Maaf, saya adalah asisten Program Bantuan Santri yang fokus pada topik santri, pesantren, pendidikan, dan bantuan sosial. Saya tidak dapat membahas topik memasak. Apakah ada yang ingin Anda tanyakan seputar santri, pesantren, atau program bantuan?",
    "model": "gemini-2.0-flash-exp"
  }
}
```

## Testing

Script test tersedia di `test_gemini_ask.py`. Untuk menjalankan test:

```bash
# Pastikan server FastAPI berjalan di port 8000
uvicorn app.main:app --reload

# Di terminal lain, jalankan test script
python test_gemini_ask.py
```

Test script akan menguji berbagai skenario:
1. Pertanyaan valid tentang pesantren
2. Pertanyaan valid tentang Hari Santri
3. Pertanyaan valid tentang bantuan sosial
4. Pertanyaan valid tentang kitab kuning
5. Pertanyaan tentang politik (harus ditolak)
6. Pertanyaan tentang perbandingan agama (harus ditolak)
7. Pertanyaan di luar topik (harus diarahkan)
8. Pertanyaan valid tentang NU

## Integrasi dengan Frontend

### React/Next.js Example

```typescript
async function askQuestion(question: string) {
  const response = await fetch('http://localhost:8000/gemini/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error('Failed to get answer');
  }

  const data = await response.json();
  return data.data.answer;
}

// Usage
const answer = await askQuestion('Apa itu pesantren?');
console.log(answer);
```

### JavaScript/Fetch Example

```javascript
document.getElementById('askButton').addEventListener('click', async () => {
  const question = document.getElementById('questionInput').value;
  
  try {
    const response = await fetch('http://localhost:8000/gemini/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    
    if (data.status === 'success') {
      document.getElementById('answer').textContent = data.data.answer;
    }
  } catch (error) {
    console.error('Error:', error);
  }
});
```

## System Instruction

Endpoint ini menggunakan system instruction yang telah dikonfigurasi untuk:

1. **Identitas**: Memperkenalkan diri sebagai "Asisten Program Bantuan Santri"
2. **Batasan Topik**: Hanya membahas topik yang relevan dengan santri, pesantren, dan program bantuan
3. **Penolakan Sopan**: Menolak pertanyaan di luar topik dengan cara yang sopan dan mengarahkan kembali
4. **Objektif**: Memberikan jawaban yang objektif dan berdasarkan fakta
5. **Bahasa**: Menggunakan bahasa Indonesia yang baik dan benar
6. **Etika**: Menghormati keberagaman dan menghindari bias

## Konfigurasi

Endpoint ini menggunakan konfigurasi Gemini dari environment variables:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.7
```

## Limitasi

1. **Rate Limiting**: Tergantung pada quota API Gemini yang digunakan
2. **Panjang Pertanyaan**: Maksimal 1000 karakter
3. **Panjang Jawaban**: Tergantung pada model Gemini yang digunakan
4. **Bahasa**: Dioptimalkan untuk Bahasa Indonesia
5. **Konteks**: Tidak menyimpan riwayat percakapan (stateless)

## Troubleshooting

### Error: "GEMINI_API_KEY not configured"

**Solusi**: Pastikan environment variable `GEMINI_API_KEY` sudah diset di file `.env`

### Error: "google-genai package not installed"

**Solusi**: Install package dengan `pip install google-genai`

### Response lambat

**Kemungkinan penyebab**:
- Koneksi internet lambat
- API Gemini sedang sibuk
- Pertanyaan terlalu kompleks

**Solusi**: 
- Cek koneksi internet
- Coba lagi beberapa saat kemudian
- Sederhanakan pertanyaan

## Best Practices

1. **Pertanyaan Spesifik**: Ajukan pertanyaan yang spesifik untuk mendapatkan jawaban yang lebih akurat
2. **Konteks Jelas**: Berikan konteks yang jelas dalam pertanyaan
3. **Bahasa Formal**: Gunakan bahasa Indonesia yang baik untuk hasil optimal
4. **Verifikasi**: Selalu verifikasi informasi penting dari sumber resmi
5. **Error Handling**: Implementasikan error handling yang baik di frontend

## Changelog

### Version 1.0.0 (2026-01-17)
- Initial release
- Implementasi endpoint `/gemini/ask`
- System instruction untuk pembatasan topik
- Validasi input dengan Pydantic
- Dokumentasi lengkap
- Test script

## Lisensi

Endpoint ini adalah bagian dari aplikasi Program Bantuan Santri dan mengikuti lisensi yang sama dengan aplikasi utama.
