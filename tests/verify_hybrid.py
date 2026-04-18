import requests
import os

def test_switch():
    print("🚀 Verifierar motor-switch...")
    # Test Piper
    res1 = requests.post("http://localhost:8000/process", json={"prompt": "Hej piper", "engine": "piper"})
    assert res1.status_code == 200
    print("✅ Piper vald")
    
    # Test MMS
    res2 = requests.post("http://localhost:8000/process", json={"prompt": "Hej mms", "engine": "mms"})
    assert res2.status_code == 200
    print("✅ MMS vald")

if __name__ == "__main__":
    # Servern måste köras i bakgrunden för detta test
    test_switch()
