# API Keys & Environment Variables Setup

## 🔐 Aman Menyimpan API Keys

### 1. **Development (Local)**

#### Langkah 1: Copy `.env.example` ke `.env`
```bash
cp .env.example .env
```

#### Langkah 2: Edit `.env` dan masukkan API key Anda
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.3
```

#### Langkah 3: Pastikan `.env` di `.gitignore`
File `.gitignore` sudah include:
```
.env
.env.local
```

**PENTING:** Jangan commit `.env` ke Git!

---

### 2. **Production (Server/Docker)**

#### Option A: Environment Variables langsung
```bash
export OPENAI_API_KEY=sk-your-api-key
export OPENAI_MODEL=gpt-4-turbo
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Option B: Docker `.env` file (di server saja, not in repo)
```dockerfile
# File .env di server (tidak di Git)
OPENAI_API_KEY=sk-prod-key-here
```

#### Option C: GitHub Secrets (untuk CI/CD)
```yaml
# .github/workflows/deploy.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

### 3. **Konfigurasi Loading**

File `app/core/config.py` sudah setup untuk load dari `.env`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TEMPERATURE: float = 0.3
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

#### Usage di code:
```python
from app.core.config import settings

api_key = settings.OPENAI_API_KEY
model = settings.OPENAI_MODEL
```

---

## ✅ Checklist Keamanan

- [ ] `.env` sudah di `.gitignore`
- [ ] `.env.example` commit ke repo (tanpa key asli)
- [ ] OPENAI_API_KEY sudah diisi di `.env` local
- [ ] Jangan share `.env` file ke siapapun
- [ ] Ganti API key jika accidentally leak
- [ ] Use environment variables di production
- [ ] Jangan hardcode secrets di code

---

## 📝 Dapatkan OpenAI API Key

1. Buka https://platform.openai.com/api-keys
2. Login dengan akun OpenAI Anda
3. Klik "Create new secret key"
4. Copy key yang muncul
5. Paste ke dalam `.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

---

## 🚀 Test Configuration

```bash
python -c "from app.core.config import settings; print(f'API Key loaded: {settings.OPENAI_API_KEY[:20]}...')"
```

Output:
```
API Key loaded: sk-proj-abc123def456...
```

---

## ⚠️ Troubleshooting

**Error: "OPENAI_API_KEY not set"**
- Check `.env` file exists
- Verify key format: `sk-...`
- Restart terminal/IDE

**Error: "python-dotenv not installed"**
```bash
pip install python-dotenv
```

---

**Happy coding! 🎉**
