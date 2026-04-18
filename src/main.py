import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from src.tts_engine import MMSLoader
import scipy.io.wavfile as wavfile
import os

app = FastAPI()
loader = MMSLoader()
# Se till att modellen är laddad (initierad i __init__ för enkelhetens skull)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/tts")
async def tts(text: str):
    try:
        inputs = loader.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = loader.model(**inputs)
        
        audio = output.waveform[0].numpy()
        
        os.makedirs("audio_out", exist_ok=True)
        output_path = "audio_out/output.wav"
        wavfile.write(output_path, loader.model.config.sampling_rate, audio)
        
        return FileResponse(output_path, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
