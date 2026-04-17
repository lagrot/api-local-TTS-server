import os
import re
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

# Om du kör AMD via ROCm i WSL2 kommer torch.cuda.is_available() vara True.
# Annars körs XTTS på CPU, vilket är långsammare men ger samma höga kvalitet.

if not os.path.exists("models"):
    os.makedirs("models")

if not os.path.exists(LLM_MODEL_PATH):
    print(f"VARNING: Hittade inte modellen på {LLM_MODEL_PATH}. Se till att flytta din .gguf-fil till models/ mappen.")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

app = FastAPI(title="AMD AI Voice API - Llama 3 & XTTS-v2")

# --- Initiera LLM ---
print("Laddar Llama-3 till GPU (Vulkan)...")
llm = Llama(
    model_path=LLM_MODEL_PATH,
    n_gpu_layers=-1, # Skicka allt till 6700 XT
    n_ctx=2048,
    verbose=False
)

# --- Initiera TTS (XTTS-v2) ---
print(f"Laddar XTTS-v2 till {DEVICE}...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

class Query(BaseModel):
    prompt: str = Field(..., example="Berätta en kort historia om en riddare.")

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def clean_text_for_speech(text: str) -> str:
    """Tar bort asterisker och andra specialtecken som Piper inte ska uttala."""
    # Tar bort * (vanligt för emotioner/stil i LLM-svar)
    text = text.replace("*", "")
    # Tar bort hash-tecken och extra whitespace
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_llama3_prompt(user_prompt: str) -> str:
    """Formatterar enligt Llama 3 Chat Template."""
    system_prompt = "Du är en hjälpsam assistent. Svara alltid kortfattat och på svenska."
    
    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

@app.post("/generate")
async def generate_text(query: Query):
    """Genererar svensk text med Llama 3."""
    try:
        formatted_prompt = format_llama3_prompt(query.prompt)
        
        # Kör synkron LLM-generering i en threadpool för att inte låsa API:et
        response = await run_in_threadpool(
            llm,
            formatted_prompt,
            max_tokens=256,
            stop=["<|eot_id|>", "<|start_header_id|>", "assistant"],
            echo=False
        )
        
        text = response["choices"][0]["text"].strip()
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speak")
async def text_to_speech(query: Query, background_tasks: BackgroundTasks):
    """Omvandlar text till tal via XTTS-v2."""
    try:
        file_name = "speech_output.wav"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        cleaned_text = clean_text_for_speech(query.prompt)

        # XTTS kräver en referensröst (speaker) eller en ljudfil för röstkloning.
        # Vi använder den inbyggda 'Daisy' eller liknande som standard.
        await run_in_threadpool(
            tts.tts_to_file,
            text=cleaned_text,
            speaker="Daisy",  # Eller använd en specifik röstprofil
            language="sv",
            file_path=file_path
        )

        # Ta bort filen efter att den skickats för att inte skräpa ner
        background_tasks.add_task(remove_file, file_path)

        return FileResponse(
            file_path, 
            media_type="audio/wav", 
            filename=file_name,
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def full_process(query: Query):
    """Full pipeline: Fråga -> LLM -> TTS."""
    # 1. Generera text
    res = await generate_text(query)
    generated_text = res["text"]
    
    # 2. Skicka den genererade texten till TTS (vi skapar ett nytt Query-objekt internt)
    # Notera: Vi returnerar texten så användaren ser vad som sas
    return {
        "text": generated_text,
        "audio_url": "/speak" # I en riktig app skulle man kunna spara unika filer
    }

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000)
