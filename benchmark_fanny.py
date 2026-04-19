import requests

# Kör ett anrop med Fanny-profil
url = "http://localhost:8000/tts_direct"
payload = {
    "text": "Detta är ett test av röstkloningen med Fanny-profilen.",
    "reference_audio": "fanny"
}

print("Triggar inferens...")
response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print("Inferens klar. Kontrollera serverns loggar för prestanda-data.")
