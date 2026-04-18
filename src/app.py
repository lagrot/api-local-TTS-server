import os
import re
import uuid
import httpx
import torch
import logging
import subprocess
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from TTS.api import TTS

# --- Konfiguration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"
# Vi använder /dev/shm (RAM-disk på Linux) för extrem hastighet
RAM_DIR = "/dev/shm/api_audio"
os.makedirs(RAM_DIR, exist_ok=True)

# Agree to Coqui license automatically
os.environ["COQUI_TOS_AGREED"] = "1"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd-ai-api")

# --- GPU Detection ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE} for TTS.")

app = FastAPI(title="AMD AI Voice API - Ollama & RAM-MP3")

# --- Global State ---
tts = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia om en riddare."})
    speaker: str = Field("Daisy", description="Namnet på rösten.")
    model: str = Field(OLLAMA_MODEL, description="Ollama-modell.")
    bitrate: str = Field("320k", description="MP3 bitrate (t.ex. 128k, 256k, 320k).")

def get_tts():
    global tts
    if tts is None:
        logger.info(f"Loading XTTS-v2 to {DEVICE}...")
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
        except Exception as e:
            logger.error(f"Failed to load TTS: {e}")
            raise HTTPException(status_code=500, detail="TTS Model loading failed")
    return tts

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    # Ta bort <think> block (DeepSeek-R1)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Ta bort asterisker och annat skräp
    text = text.replace("*", "").replace("_", "")
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "320k"):
    """Konverterar WAV till MP3 i hög kvalitet med ffmpeg."""
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
        "gpu_available": torch.cuda.is_available(),
        "tts_loaded": tts is not None,
        "ram_disk_ready": os.path.exists(RAM_DIR)
    }

@app.post("/generate")
async def generate_text(query: Query):
    try:
        # Ökad timeout till 180s för DeepSeek-R1 modeller
        async with httpx.AsyncClient(timeout=180.0) as client:
            payload = {
                "model": query.model,
                "prompt": f"Du är en hjälpsam assistent. Svara alltid på svenska. {query.prompt}",
                "stream": False
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return {"text": result["response"].strip()}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama server is not reachable on localhost:11434")
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    # 1. Generera Text via Ollama
    gen_res = await generate_text(query)
    text_response = gen_res["text"]
    cleaned_text = clean_text_for_speech(text_response)
    
    if not cleaned_text:
        raise HTTPException(status_code=500, detail="Empty text response from LLM")

    # 2. Generera WAV i RAM
    tts_model = get_tts()
    file_id = str(uuid.uuid4())
    wav_path = os.path.join(RAM_DIR, f"{file_id}.wav")
    mp3_path = os.path.join(RAM_DIR, f"{file_id}.mp3")
    
    try:
        # XTTS-v2 genererar WAV
        await run_in_threadpool(
            tts_model.tts_to_file,
            text=cleaned_text,
            speaker=query.speaker,
            language="sv",
            file_path=wav_path
        )
        
        # 3. Konvertera till MP3 i RAM
        if not convert_to_mp3(wav_path, mp3_path, query.bitrate):
            raise HTTPException(status_code=500, detail="MP3 conversion failed")

        # Rensa WAV direkt
        remove_file(wav_path)
        
        # 4. Returnera MP3 och städa efteråt
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
