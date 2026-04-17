import os
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from llama_cpp import Llama
from TTS.api import TTS

# --- Konfiguration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "Meta-Llama-3-8B-Instruct.Q5_K_M.gguf")
OUT_DIR = os.path.join(BASE_DIR, "audio_out")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu" # ROCm/Vulkan mappas ofta som 'cuda' i PyTorch

app = FastAPI(title="Swedish AI Voice Server")

# Globala variabler för modeller
llm = None
tts_model = None

@app.on_event("startup")
def load_models():
    global llm, tts_model
    print(f"Laddar Llama-3 på {DEVICE}...")
    # Vi lämnar lite VRAM till XTTS genom att inte maxa n_gpu_layers om det behövs,
    # men 12GB bör klara n_gpu_layers=-1 för en Q5-modell.
    llm = Llama(model_path=MODEL_PATH, n_gpu_layers=-1, n_ctx=2048, verbose=False)
    
    print(f"Laddar XTTS-v2 på {DEVICE}...")
    tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

class ChatRequest(BaseModel):
    text: str
    language: str = "sv"

@app.post("/generate")
async def generate(req: ChatRequest):
    if not llm: raise HTTPException(503, "Modell ej laddad")
    prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{req.text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    res = llm(prompt, max_tokens=150, stop=["<|eot_id|>"])
    return {"text": res["choices"][0]["text"].strip()}

@app.post("/speak")
async def speak(req: ChatRequest):
    output_path = os.path.join(OUT_DIR, "output.wav")
    try:
        # XTTS behöver en referensröst. Du kan lägga en kort .wav i models/ för att klona.
        # Här använder vi en inbyggd röst som fallback.
        tts_model.tts_to_file(
            text=req.text,
            speaker="Ana Paula 80", # En bra standardröst, byt gärna till egen .wav
            language=req.language,
            file_path=output_path
        )
        return FileResponse(output_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(500, f"TTS-fel: {str(e)}")

@app.post("/process")
async def process(req: ChatRequest):
    text_res = await generate(req)
    audio_res = await speak(ChatRequest(text=text_res["text"]))
    return {"text": text_res["text"], "audio": "/audio_out/output.wav"}