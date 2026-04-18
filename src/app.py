import os
import re
import uuid
import torch
import logging
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from llama_cpp import Llama
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from TTS.api import TTS

# --- Setup Environment for ROCm/Coqui ---
# Agree to Coqui license automatically to prevent terminal hang
os.environ["COQUI_TOS_AGREED"] = "1"
# Override for RX 6700 XT (Navi 22 / gfx1031) if needed by ROCm
if "HSA_OVERRIDE_GFX_VERSION" not in os.environ:
    os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd-ai-api")

# --- Konfiguration ---
LLM_MODEL_PATH = "models/Meta-Llama-3-8B-Instruct.Q5_K_M.gguf"
OUTPUT_DIR = "audio_out"

# Better GPU Detection
def get_device_info():
    available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if available else "None"
    hip_version = getattr(torch.version, 'hip', 'N/A')
    return available, device_name, hip_version

GPU_AVAILABLE, DEVICE_NAME, HIP_VERSION = get_device_info()
DEVICE = "cuda" if GPU_AVAILABLE else "cpu"

if GPU_AVAILABLE:
    logger.info(f"AMD GPU Detected via ROCm: {DEVICE_NAME} (HIP: {HIP_VERSION})")
else:
    logger.warning("No AMD GPU detected via PyTorch ROCm backend. Using CPU.")

# Ensure directories exist
os.makedirs("models", exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="AMD AI Voice API - Llama 3 & XTTS-v2")

# --- Global State ---
llm = None
tts = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia om en riddare."})
    speaker: str = Field("Daisy", description="Namnet på rösten som ska användas (t.ex. Daisy, Viktor, Ana).")

def init_llm():
    if not os.path.exists(LLM_MODEL_PATH):
        logger.error(f"Model not found at {LLM_MODEL_PATH}")
        return None
    
    try:
        logger.info(f"Loading Llama-3 from {LLM_MODEL_PATH}...")
        # If GPU_AVAILABLE is false, n_gpu_layers=-1 will still work but use CPU if backend is missing
        return Llama(
            model_path=LLM_MODEL_PATH,
            n_gpu_layers=-1, 
            n_ctx=2048,
            verbose=False
        )
    except Exception as e:
        logger.error(f"Failed to load LLM: {e}")
        return None

def get_tts():
    global tts
    if tts is None:
        logger.info(f"Loading XTTS-v2 to {DEVICE}...")
        try:
            # XTTS-v2 model will download automatically on first run if not present
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
        except Exception as e:
            logger.error(f"Failed to load TTS: {e}")
            raise HTTPException(status_code=500, detail="TTS Model loading failed")
    return tts

@app.on_event("startup")
async def startup_event():
    global llm
    llm = init_llm()

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    text = text.replace("*", "")
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_llama3_prompt(user_prompt: str) -> str:
    system_prompt = "Du är en hjälpsam assistent. Svara alltid kortfattat och på svenska."
    return (
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

@app.get("/health")
async def health_check():
    gpu_ok, dev_name, hip_ver = get_device_info()
    return {
        "status": "online",
        "gpu_available": gpu_ok,
        "gpu_device": dev_name,
        "hip_version": hip_ver,
        "llm_loaded": llm is not None,
        "tts_loaded": tts is not None,
        "os_env_gfx": os.environ.get("HSA_OVERRIDE_GFX_VERSION", "Not Set")
    }

@app.get("/speakers")
async def list_speakers():
    tts_model = get_tts()
    try:
        return {"speakers": tts_model.speakers}
    except Exception as e:
        logger.error(f"Failed to list speakers: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve speaker list")

@app.post("/generate")
async def generate_text(query: Query):
    if llm is None:
        raise HTTPException(status_code=503, detail="LLM not loaded. Check if model file exists in models/")
    
    try:
        formatted_prompt = format_llama3_prompt(query.prompt)
        response = await run_in_threadpool(
            llm,
            formatted_prompt,
            max_tokens=256,
            stop=["<|eot_id|>", "<|start_header_id|>"],
            echo=False
        )
        return {"text": response["choices"][0]["text"].strip()}
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=400, detail=f"TTS error: {str(e)}. Tip: Check /speakers for valid names.")

@app.post("/process")
async def full_process(query: Query, background_tasks: BackgroundTasks):
    gen_res = await generate_text(query)
    text_response = gen_res["text"]
    
    tts_model = get_tts()
    file_id = str(uuid.uuid4())
    file_path = os.path.join(OUTPUT_DIR, f"full_{file_id}.wav")
    
    await run_in_threadpool(
        tts_model.tts_to_file,
        text=clean_text_for_speech(text_response),
        speaker=query.speaker,
        language="sv",
        file_path=file_path
    )
    
    background_tasks.add_task(remove_file, file_path)
    
    return FileResponse(
        file_path, 
        media_type="audio/wav", 
        headers={"X-Generated-Text": text_response.encode('utf-8').decode('latin-1')} 
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
