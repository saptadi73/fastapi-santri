"""
Contoh sederhana penggunaan endpoint Gemini Ask Question
"""

# Contoh 1: Menggunakan requests library
def example_with_requests():
    import requests
    
    url = "http://localhost:8000/gemini/ask"
    
    # Pertanyaan tentang pesantren
    payload = {
        "question": "Apa itu pesantren dan bagaimana sistem pendidikannya?"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Pertanyaan:", data['data']['question'])
        print("\nJawaban:", data['data']['answer'])
    else:
        print("Error:", response.status_code)
        print(response.text)


# Contoh 2: Menggunakan httpx (async)
async def example_with_httpx():
    import httpx
    
    url = "http://localhost:8000/gemini/ask"
    
    # Pertanyaan tentang Hari Santri
    payload = {
        "question": "Bagaimana sejarah Hari Santri di Indonesia?"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("Pertanyaan:", data['data']['question'])
            print("\nJawaban:", data['data']['answer'])
        else:
            print("Error:", response.status_code)
            print(response.text)


# Contoh 3: Menggunakan curl (command line)
curl_example = """
# Contoh menggunakan curl di terminal/command line:

curl -X POST "http://localhost:8000/gemini/ask" \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "Apa peran Nahdlatul Ulama dalam pendidikan pesantren?"
  }'
"""


# Contoh 4: Interactive CLI
def interactive_cli():
    import requests
    
    print("=" * 60)
    print("ASISTEN PROGRAM BANTUAN SANTRI")
    print("=" * 60)
    print("\nTanya jawab tentang santri, pesantren, dan program bantuan")
    print("Ketik 'exit' untuk keluar\n")
    
    url = "http://localhost:8000/gemini/ask"
    
    while True:
        question = input("\nPertanyaan Anda: ")
        
        if question.lower() == 'exit':
            print("\nTerima kasih telah menggunakan asisten!")
            break
        
        if len(question) < 5:
            print("Pertanyaan terlalu pendek. Minimal 5 karakter.")
            continue
        
        try:
            response = requests.post(url, json={"question": question})
            
            if response.status_code == 200:
                data = response.json()
                print("\n" + "=" * 60)
                print("JAWABAN:")
                print("=" * 60)
                print(data['data']['answer'])
            else:
                print(f"\nError {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Pastikan server FastAPI berjalan di http://localhost:8000")


if __name__ == "__main__":
    print("\nPilih contoh yang ingin dijalankan:")
    print("1. Contoh dengan requests (sync)")
    print("2. Contoh dengan httpx (async)")
    print("3. Lihat contoh curl")
    print("4. Mode interaktif")
    
    choice = input("\nPilihan (1-4): ")
    
    if choice == "1":
        print("\nMenjalankan contoh dengan requests...")
        example_with_requests()
    elif choice == "2":
        print("\nMenjalankan contoh dengan httpx...")
        import asyncio
        asyncio.run(example_with_httpx())
    elif choice == "3":
        print(curl_example)
    elif choice == "4":
        interactive_cli()
    else:
        print("Pilihan tidak valid")
