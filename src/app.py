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
# Ollama körs på GPU och hanterar LLM-delen
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"
# Piper körs på CPU och hanterar rösten blixtsnabbt
MODEL_PATH = "models/piper/sv_SE-alby-medium.onnx"
# Vi använder /dev/shm (RAM-disk på Linux) för extrem hastighet
RAM_DIR = "/dev/shm/api_audio"
os.makedirs(RAM_DIR, exist_ok=True)

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd-ai-api")

app = FastAPI(title="AMD AI Voice API - Stable Swedish (Ollama + Piper)")

# --- Global State ---
voice = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia."})
    model: str = Field(OLLAMA_MODEL, description="Ollama-modell att använda.")
    bitrate: str = Field("320k", description="MP3 bitrate för ljudkvalitet.")

def get_voice():
    global voice
    if voice is None:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Piper model not found at {MODEL_PATH}")
            raise HTTPException(status_code=500, detail="Voice model missing. Run setup.sh first.")
        
        logger.info(f"Loading Piper voice from {MODEL_PATH}...")
        try:
            voice = PiperVoice.load(MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to load Piper voice: {e}")
            raise HTTPException(status_code=500, detail="Voice model loading failed")
    return voice

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    # Ta bort <think> block från DeepSeek-R1
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Ta bort formatering som asterisker och hashtags
    text = text.replace("*", "").replace("_", "").replace("#", "")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "320k"):
    """Konverterar WAV till högkvalitativ MP3 i RAM-disken."""
    try:
        cmd = [
            "ffmpeg", "-y", "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            mp3_path
        ]
        # Kör FFmpeg tyst för att undvika log-spam
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        logger.error(f"FFmpeg conversion failed: {e}")
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "llm_backend": "Ollama (GPU)",
        "tts_engine": "Piper (CPU-Stable)",
        "voice_loaded": voice is not None,
        "ram_disk_ready": os.path.exists(RAM_DIR)
    }

@app.post("/generate")
async def generate_text(query: Query):
    try:
        # Ökad timeout för tyngre R1 modeller
        async with httpx.AsyncClient(timeout=180.0) as client:
            payload = {
                "model": query.model,
                "prompt": f"Du är en hjälpsam assistent. Svara alltid kort och koncist på svenska. {query.prompt}",
                "stream": False
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return {"text": result["response"].strip()}
    except Exception as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail="Ollama backend is currently unavailable.")

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    # 1. Hämta svar från Ollama (GPU)
    gen_res = await generate_text(query)
    text_response = gen_res["text"]
    cleaned_text = clean_text_for_speech(text_response)
    
    if not cleaned_text:
        raise HTTPException(status_code=500, detail="Empty text response from LLM")

    # 2. Skapa ljud i RAM (/dev/shm)
    voice_engine = get_voice()
    file_id = str(uuid.uuid4())
    wav_path = os.path.join(RAM_DIR, f"{file_id}.wav")
    mp3_path = os.path.join(RAM_DIR, f"{file_id}.mp3")
    
    try:
        # Piper skapar WAV-fil
        with wave.open(wav_path, "wb") as wav_file:
            voice_engine.synthesize(cleaned_text, wav_file)
        
        # 3. Konvertera till 320kbps MP3
        if not convert_to_mp3(wav_path, mp3_path, query.bitrate):
            raise HTTPException(status_code=500, detail="MP3 conversion failed")

        # Rensa WAV direkt, MP3 rensas efter responsen
        remove_file(wav_path)
        background_tasks.add_task(remove_file, mp3_path)
        
        return FileResponse(
            mp3_path, 
            media_type="audio/mpeg", 
            filename="output.mp3",
            headers={"X-Generated-Text": cleaned_text.encode('utf-8').decode('latin-1')} 
        )
    except Exception as e:
        logger.error(f"Full process failure: {e}")
        if os.path.exists(wav_path): remove_file(wav_path)
        if os.path.exists(mp3_path): remove_file(mp3_path)
        raise HTTPException(status_code=500, detail="Audio generation failed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
