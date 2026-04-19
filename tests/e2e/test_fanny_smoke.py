import pytest
import requests
import os

def test_fanny_smoke():
    """
    E2E Smoke-test: Verifierar att Fanny-profilen genererar en giltig ljudfil.
    Detta test körs mot en körande server (förutsätter att servern startats med ./run_server.sh).
    """
    url = "http://localhost:8000/tts_direct"
    payload = {
        "text": "Detta är ett E2E smoke-test för att verifiera Fanny-rösten.",
        "reference_audio": "fanny"
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        assert response.status_code == 200, f"Servern returnerade {response.status_code}"
        
        # Spara tillfällig fil
        output_file = "tests/e2e/smoke_test.mp3"
        with open(output_file, "wb") as f:
            f.write(response.content)
            
        # Verifiera att filen inte är tom (minst 10kB för att vara säker på att det inte är brus)
        assert os.path.getsize(output_file) > 10000, "Ljudfilen är för liten eller tom!"
        
    finally:
        if os.path.exists("tests/e2e/smoke_test.mp3"):
            os.remove("tests/e2e/smoke_test.mp3")
