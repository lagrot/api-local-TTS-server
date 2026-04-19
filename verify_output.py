import requests

# Kör ett anrop med Fanny-profil och spara som en riktig fil
url = "http://localhost:8000/tts_direct"
payload = {
    "text": "Detta är ett verifieringstest för att höra Fanny-rösten. Nu önskar vi dig en avkopplande och njutbar resa.",
    "reference_audio": "fanny"
}

print("Genererar ljud via servern...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    output_file = "audio_out/verification_fanny.mp3"
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"Ljud genererat och sparat till: {output_file}")
else:
    print(f"Fel vid generering: {response.status_code}")
    print(response.text)
