import os
import re
import uuid
import httpx
import logging
import subprocess
import wave
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from piper.voice import PiperVoice

# --- Konfiguration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"
# Vi använder Piper för bästa svenska röstkvalitet och stabilitet
MODEL_PATH = "models/piper/sv_SE-tbatch-medium.onnx"
RAM_DIR = "/dev/shm/api_audio"
os.makedirs(RAM_DIR, exist_ok=True)

# Setup Environment
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd-ai-api")

app = FastAPI(title="AMD AI Voice API - Piper (Best Swedish)")

# --- Global State ---
voice = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en historia."})
    model: str = Field(OLLAMA_MODEL, description="Ollama-modell.")
    bitrate: str = Field("320k", description="MP3 bitrate.")

def get_voice():
    global voice
    if voice is None:
        logger.info(f"Loading Piper voice from {MODEL_PATH}...")
        try:
            # Piper körs extremt snabbt på CPU eller GPU via ONNX
            voice = PiperVoice.load(MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to load Piper voice: {e}")
            raise HTTPException(status_code=500, detail="Voice model loading failed")
    return voice

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = text.replace("*", "").replace("_", "")
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "320k"):
    try:
        cmd = [
            "ffmpeg", "-y", "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            mp3_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        logger.error(f"FFmpeg conversion failed: {e}")
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "engine": "Piper",
        "voice_loaded": voice is not None,
        "ram_disk_ready": os.path.exists(RAM_DIR)
    }

@app.post("/generate")
async def generate_text(query: Query):
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            payload = {
                "model": query.model,
                "prompt": f"Du är en hjälpsam assistent. Svara kort på svenska. {query.prompt}",
                "stream": False
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return {"text": result["response"].strip()}
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    gen_res = await generate_text(query)
    text_response = gen_res["text"]
    cleaned_text = clean_text_for_speech(text_response)
    
    if not cleaned_text:
        raise HTTPException(status_code=500, detail="Empty text response from LLM")

    voice_engine = get_voice()
    file_id = str(uuid.uuid4())
    wav_path = os.path.join(RAM_DIR, f"{file_id}.wav")
    mp3_path = os.path.join(RAM_DIR, f"{file_id}.mp3")
    
    try:
        # Generera WAV direkt i RAM med Piper
        with wave.open(wav_path, "wb") as wav_file:
            # Piper genererar rå ljudström
            voice_engine.synthesize(cleaned_text, wav_file)
        
        # Konvertera till MP3
        if not convert_to_mp3(wav_path, mp3_path, query.bitrate):
            raise HTTPException(status_code=500, detail="MP3 conversion failed")

        remove_file(wav_path)
        background_tasks.add_task(remove_file, mp3_path)
        
        return FileResponse(
            mp3_path, 
            media_type="audio/mpeg", 
            filename="output.mp3",
            headers={"X-Generated-Text": cleaned_text.encode('utf-8').decode('latin-1')} 
        )
    except Exception as e:
        logger.error(f"Process error: {e}")
        if os.path.exists(wav_path): remove_file(wav_path)
        if os.path.exists(mp3_path): remove_file(mp3_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
