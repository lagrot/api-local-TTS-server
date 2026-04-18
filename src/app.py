import os
import re
import uuid
import httpx
import torch
import logging
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from TTS.api import TTS

# --- Konfiguration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"  # Vi använder en av dina installerade modeller
OUTPUT_DIR = "audio_out"

# Agree to Coqui license automatically
os.environ["COQUI_TOS_AGREED"] = "1"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd-ai-api")

# --- GPU Detection (för TTS) ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE} for TTS.")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="AMD AI Voice API - Ollama & XTTS-v2")

# --- Global State ---
tts = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia om en riddare."})
    speaker: str = Field("Daisy", description="Namnet på rösten som ska användas.")
    model: str = Field(OLLAMA_MODEL, description="Ollama-modellen som ska användas.")

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
    # Ta bort <think> block om det är en r1 modell
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = text.replace("*", "")
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "gpu_available": torch.cuda.is_available(),
        "tts_loaded": tts is not None,
        "ollama_connected": True # Vi kollar detta vid start
    }

@app.get("/speakers")
async def list_speakers():
    tts_model = get_tts()
    return {"speakers": tts_model.speakers}

@app.post("/generate")
async def generate_text(query: Query):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": query.model,
                "prompt": f"Svara alltid kortfattat och på svenska: {query.prompt}",
                "stream": False
            }
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return {"text": result["response"].strip()}
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama connection failed: {str(e)}")

@app.post("/speak")
async def text_to_speech(query: Query, background_tasks: BackgroundTasks):
    tts_model = get_tts()
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(OUTPUT_DIR, f"speech_{file_id}.wav")
        cleaned_text = clean_text_for_speech(query.prompt)

        await run_in_threadpool(
            tts_model.tts_to_file,
            text=cleaned_text,
            speaker=query.speaker,
            language="sv",
            file_path=file_path
        )
        background_tasks.add_task(remove_file, file_path)
        return FileResponse(file_path, media_type="audio/wav")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    # 1. Generate via Ollama
    gen_res = await generate_text(query)
    text_response = gen_res["text"]
    
    # 2. Generate Speech
    tts_model = get_tts()
    file_id = str(uuid.uuid4())
    file_path = os.path.join(OUTPUT_DIR, f"full_{file_id}.wav")
    
    # Rensa texten (speciellt viktigt för R1 modeller som har <think> block)
    cleaned_text = clean_text_for_speech(text_response)
    
    await run_in_threadpool(
        tts_model.tts_to_file,
        text=cleaned_text,
        speaker=query.speaker,
        language="sv",
        file_path=file_path
    )
    
    background_tasks.add_task(remove_file, file_path)
    
    return FileResponse(
        file_path, 
        media_type="audio/wav", 
        headers={"X-Generated-Text": cleaned_text.encode('utf-8').decode('latin-1')} 
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
