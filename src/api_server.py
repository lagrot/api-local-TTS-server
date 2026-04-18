from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.tts_engine import generate_audio as piper_audio
from src.tts_engine_mms import generate_audio as mms_audio
import uuid
import os

app = FastAPI(title="AMD AI Voice API")

class Query(BaseModel):
    prompt: str
    model: str = "ai-sweden-llama3"
    bitrate: str = "128k"
    engine: str = "piper" # piper eller mms

@app.get("/health")
def health():
    return {"status": "online"}

@app.post("/process")
def process(query: Query):
    # LLM-anrop (Ollama)
    import httpx, re
    try:
        resp = httpx.post("http://localhost:11434/api/chat", json={
            "model": query.model,
            "messages": [{"role": "user", "content": f"Svara naturligt på svenska: {query.prompt}"}],
            "stream": False
        }, timeout=60.0)
        text = re.sub(r'<think>.*?</think>', '', resp.json()["message"]["content"], flags=re.DOTALL).replace("*", "").replace("#", "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {e}")

    # Motor-switch
    file_id = str(uuid.uuid4())
    output_path = os.path.join("audio_out", f"{file_id}.mp3")
    
    try:
        if query.engine == "mms":
            mms_audio(text, output_path)
        else:
            piper_audio(text, output_path, bitrate=query.bitrate)
        return {"file": output_path, "status": "success", "engine": query.engine}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine Error: {e}")
