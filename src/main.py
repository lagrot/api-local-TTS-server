import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.tts_engine import MMSLoader
from src.llm_engine import OllamaClient
import scipy.io.wavfile as wavfile
import io
import subprocess
import os

app = FastAPI()
loader = MMSLoader()
llm = OllamaClient()

class ChatRequest(BaseModel):
    prompt: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # 1. Hämta text från LLM
        text_response = await llm.generate_text(request.prompt)
        
        # 2. Generera tal från MMS
        inputs = loader.tokenizer(text_response, return_tensors="pt").to(loader.device)
        with torch.no_grad():
            output = loader.model(**inputs)
        
        audio = output.waveform[0].cpu().numpy()
        
        # 3. Konvertera till MP3
        wav_buffer = io.BytesIO()
        wavfile.write(wav_buffer, loader.model.config.sampling_rate, audio)
        wav_buffer.seek(0)
        
        process = subprocess.Popen(
            ['ffmpeg', '-y', '-i', 'pipe:0', '-f', 'mp3', '-ab', '320k', '-ar', '48000', '-af', 'aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6', 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mp3_data, _ = process.communicate(input=wav_buffer.read())
        
        return StreamingResponse(io.BytesIO(mp3_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
