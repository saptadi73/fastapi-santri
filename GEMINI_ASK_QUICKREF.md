# Quick Reference: Endpoint Gemini Ask Question

## 📍 Endpoint
```
POST /gemini/ask
```

## 📝 Request Body
```json
{
  "question": "string (5-1000 chars)"
}
```

## ✅ Response (Success)
```json
{
  "status": "success",
  "data": {
    "success": true,
    "question": "...",
    "answer": "...",
    "model": "gemini-2.0-flash-exp"
  }
}
```

## 🎯 Topik BOLEH Dibahas
✅ Santri & kehidupan santri  
✅ Pesantren (sejarah, sistem, kurikulum)  
✅ Nahdlatul Ulama (NU)  
✅ Program bantuan sosial  
✅ Pengentasan kemiskinan  
✅ Pendidikan (formal & non-formal)  
✅ Dakwah & metode dakwah  
✅ Kitab kuning  
✅ Islam (ajaran, ibadah, akhlak)  
✅ Sejarah Islam  
✅ Sejarah pesantren  
✅ Hari Santri (22 Oktober)  
✅ Hari Pahlawan  

## 🚫 Topik TIDAK BOLEH
❌ Politik praktis  
❌ Partai politik  
❌ Perbandingan agama  

## 💡 Contoh Pertanyaan Valid
```
"Apa itu pesantren dan bagaimana sistem pendidikannya?"
"Bagaimana sejarah Hari Santri di Indonesia?"
"Apa saja program bantuan sosial untuk santri?"
"Apa peran Nahdlatul Ulama dalam pendidikan pesantren?"
"Apa itu kitab kuning dan mengapa penting?"
```

## 🚀 Quick Test (curl)
```bash
curl -X POST "http://localhost:8000/gemini/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Apa itu pesantren?"}'
```

## 📦 Python Quick Test
```python
import requests

response = requests.post(
    "http://localhost:8000/gemini/ask",
    json={"question": "Apa itu pesantren?"}
)
print(response.json()["data"]["answer"])
```

## 🔧 Environment Setup
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.7
```

## 📚 Files
- Service: `app/services/gemini_service.py`
- Router: `app/routes/gemini_routes.py`
- Test: `test_gemini_ask.py`
- Example: `example_gemini_ask.py`
- Docs: `GEMINI_ASK_ENDPOINT_GUIDE.md`

## 🎨 Identitas Asisten
```
Nama: Asisten Program Bantuan Santri
Peran: Membantu informasi seputar santri, 
       pesantren, dan program bantuan
Bahasa: Indonesia
Sifat: Objektif, edukatif, sopan
```

## ⚡ Quick Commands
```bash
# Run server
uvicorn app.main:app --reload

# Run tests
python test_gemini_ask.py

# Interactive mode
python example_gemini_ask.py

# API Docs
http://localhost:8000/docs
```

---
**Version**: 1.0.0 | **Date**: 2026-01-17
