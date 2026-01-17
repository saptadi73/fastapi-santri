"""
Test script for Gemini Ask Question endpoint
"""
import requests
import json

# Base URL - adjust if needed
BASE_URL = "http://localhost:8000"

def test_ask_question(question: str):
    """Test the ask question endpoint"""
    url = f"{BASE_URL}/gemini/ask"
    
    payload = {
        "question": question
    }
    
    print(f"\n{'='*60}")
    print(f"Testing Question: {question}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\nError Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GEMINI ASK QUESTION ENDPOINT TEST")
    print("="*60)
    
    # Test 1: Valid question about pesantren
    test_ask_question("Apa itu pesantren dan bagaimana sistem pendidikannya?")
    
    # Test 2: Valid question about Hari Santri
    test_ask_question("Bagaimana sejarah Hari Santri di Indonesia?")
    
    # Test 3: Valid question about bantuan sosial
    test_ask_question("Apa saja program bantuan sosial yang tersedia untuk santri?")
    
    # Test 4: Valid question about kitab kuning
    test_ask_question("Apa itu kitab kuning dan mengapa penting dalam pendidikan pesantren?")
    
    # Test 5: Question about politics (should be rejected)
    test_ask_question("Apa pendapat Anda tentang partai politik di Indonesia?")
    
    # Test 6: Question about religious comparison (should be rejected)
    test_ask_question("Apa perbedaan antara Islam dan agama lain?")
    
    # Test 7: Off-topic question (should be redirected)
    test_ask_question("Bagaimana cara membuat kue brownies?")
    
    # Test 8: Valid question about NU
    test_ask_question("Apa peran Nahdlatul Ulama dalam pendidikan pesantren?")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
