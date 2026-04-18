import os
import re
import uuid
import httpx
import logging
import subprocess
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from piper.voice import PiperVoice

# --- Konfiguration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")
MODEL_PATH = "models/piper/sv_SE-nst-medium.onnx"
RAM_DIR = "/dev/shm/api_audio"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

os.makedirs(RAM_DIR, exist_ok=True)

# --- Setup Logging ---
log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("amd-ai-api")

app = FastAPI(title="AMD AI Voice API - Debug Mode")

# --- Global State ---
voice = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia."})
    model: str = Field(OLLAMA_MODEL, description="Ollama-modell att använda.")
    bitrate: str = Field("320k", description="MP3 bitrate.")

def get_voice():
    global voice
    if voice is None:
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Piper model missing at {MODEL_PATH}")
            raise HTTPException(status_code=500, detail="Voice model missing.")
        
        logger.info(f"Loading Piper voice from {MODEL_PATH}...")
        try:
            voice = PiperVoice.load(MODEL_PATH)
            logger.debug("Piper voice loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Piper voice: {e}")
            raise HTTPException(status_code=500, detail="Voice model loading failed")
    return voice

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)
        logger.debug(f"Removed temporary file: {path}")

def clean_text_for_speech(text: str) -> str:
    original_len = len(text)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = text.replace("*", "").replace("_", "").replace("#", "")
    text = re.sub(r'\s+', ' ', text).strip()
    logger.debug(f"Text cleaned. Length reduced from {original_len} to {len(text)}.")
    return text

def convert_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "320k"):
    logger.debug(f"Converting {wav_path} to {mp3_path} at {bitrate}...")
    try:
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", bitrate, mp3_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
        return True
    except Exception as e:
        logger.error(f"FFmpeg process failure: {e}")
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "debug": DEBUG,
        "llm_backend": f"Ollama ({OLLAMA_MODEL})",
        "voice_model": MODEL_PATH,
        "ram_disk": RAM_DIR
    }

@app.post("/generate")
async def generate_text(query: Query):
    logger.info(f"Generating text via Ollama for prompt: {query.prompt[:50]}...")
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            payload = {
                "model": query.model,
                "prompt": f"Du är en hjälpsam assistent. Svara på svenska. {query.prompt}",
                "stream": False
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            text = response.json()["response"].strip()
            logger.debug(f"Ollama response received: {text[:100]}...")
            return {"text": text}
    except Exception as e:
        logger.error(f"Ollama failure: {e}")
        raise HTTPException(status_code=503, detail="Ollama backend unreachable.")

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    # 1. LLM
    gen_res = await generate_text(query)
    cleaned_text = clean_text_for_speech(gen_res["text"])
    
    if not cleaned_text:
        raise HTTPException(status_code=500, detail="Empty LLM response.")

    # 2. TTS
    voice_engine = get_voice()
    file_id = str(uuid.uuid4())
    wav_path = os.path.join(RAM_DIR, f"{file_id}.wav")
    mp3_path = os.path.join(RAM_DIR, f"{file_id}.mp3")
    
    try:
        logger.info("Synthesizing audio...")
        # FIX: Piper handles WAV headers, use standard open instead of wave.open
        with open(wav_path, "wb") as wav_file:
            voice_engine.synthesize(cleaned_text, wav_file)
        
        # 3. MP3
        if not convert_to_mp3(wav_path, mp3_path, query.bitrate):
            raise HTTPException(status_code=500, detail="MP3 conversion failed.")

        remove_file(wav_path)
        background_tasks.add_task(remove_file, mp3_path)
        
        logger.info(f"Process complete. Returning MP3: {mp3_path}")
        return FileResponse(
            mp3_path, 
            media_type="audio/mpeg", 
            filename="output.mp3",
            headers={"X-Generated-Text": cleaned_text.encode('utf-8').decode('latin-1')} 
        )
    except Exception as e:
        logger.error(f"Critical process failure: {e}")
        if os.path.exists(wav_path): remove_file(wav_path)
        if os.path.exists(mp3_path): remove_file(mp3_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
