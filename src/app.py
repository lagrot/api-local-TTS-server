import os
import re
import uuid
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from llama_cpp import Llama
from TTS.api import TTS
from starlette.concurrency import run_in_threadpool

# --- Konfiguration ---
LLM_MODEL_PATH = "models/Meta-Llama-3-8B-Instruct.Q5_K_M.gguf"
OUTPUT_DIR = "audio_out"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

if not os.path.exists("models"):
    os.makedirs("models")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

app = FastAPI(title="AMD AI Voice API - Llama 3 & XTTS-v2")
app.state.output_dir = OUTPUT_DIR

if not os.path.exists(LLM_MODEL_PATH):
    print(f"Warning: Model not found at {LLM_MODEL_PATH}. Ensure the file exists in the models/ directory.")

# --- Initiera LLM ---
print("Laddar Llama-3 till GPU (Vulkan)...")
llm = Llama(
    model_path=LLM_MODEL_PATH,
    n_gpu_layers=-1, # Skicka allt till 6700 XT
    n_ctx=2048,
    verbose=False
)

# --- Initiera TTS (XTTS-v2) ---
def get_tts():
    print(f"Laddar XTTS-v2 till {DEVICE}...")
    return TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
tts = None

class Query(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Berätta en kort historia om en riddare."})

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    """Tar bort asterisker och andra specialtecken."""
    text = text.replace("*", "")
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_llama3_prompt(user_prompt: str) -> str:
    """Formatterar enligt Llama 3 Chat Template."""
    system_prompt = "Du är en hjälpsam assistent. Svara alltid kortfattat och på svenska."
    return (
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

@app.post("/generate")
async def generate_text(query: Query):
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speak")
async def text_to_speech(query: Query, background_tasks: BackgroundTasks):
    global tts
    if tts is None:
        tts = get_tts()
    try:
        file_id = str(uuid.uuid4())
        file_name = f"speech_{file_id}.wav"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        cleaned_text = clean_text_for_speech(query.prompt)

        await run_in_threadpool(
            tts.tts_to_file,
            text=cleaned_text,
            speaker="Daisy",
            language="sv",
            file_path=file_path
        )
        background_tasks.add_task(remove_file, file_path)
        return FileResponse(file_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def full_process(query: Query):
    res = await generate_text(query)
    # Rensa texten innan TTS
    cleaned_text = clean_text_for_speech(res["text"])
    
    # Notera: Här behöver vi simulera eller hantera hur ljudfilen returneras/hämtas
    # För enkelhetens skull, returnerar vi texten och indikerar att tal genereras
    return {
        "text": res["text"],
        "audio_info": "Använd /speak med den renade texten för att få ljudfilen"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)