import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.tts_engine import TTSLoaderFactory
from src.llm_engine import OllamaClient
import scipy.io.wavfile as wavfile
import io
import subprocess
import os

app = FastAPI()
# Default to mms, can be changed via environment variable
model_type = os.getenv("TTS_MODEL_TYPE", "mms")
loader = TTSLoaderFactory.get_loader(model_type)
llm = OllamaClient()

class ChatRequest(BaseModel):
    prompt: str

class TTSRequest(BaseModel):
    text: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/tts")
async def tts(request: TTSRequest):
    return await generate_audio(request.text)

@app.post("/tts_direct")
async def tts_direct(request: TTSRequest):
    return await generate_audio(request.text)

@app.post("/chat")
async def chat(request: ChatRequest):
    text_response = await llm.generate_text(request.prompt)
    return await generate_audio(text_response)

async def generate_audio(text: str):
    try:
        audio = loader.generate(text)
        
        # Normalize to int16 if necessary
        if audio.dtype == 'float32':
            audio = (audio * 32767).astype('int16')
        
        wav_buffer = io.BytesIO()
        # For MMS: sampling_rate is model.config.sampling_rate. For Silero: 48000
        sr = 16000 if model_type == "mms" else 48000
        wavfile.write(wav_buffer, sr, audio)
        wav_buffer.seek(0)
        
        process = subprocess.Popen(
            ['ffmpeg', '-y', '-i', 'pipe:0', '-f', 'mp3', '-ab', '320k', '-ar', '48000', '-af', 'aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6', 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        def stream_generator():
            try:
                process.stdin.write(wav_buffer.read())
                process.stdin.close()
                while True:
                    chunk = process.stdout.read(4096)
                    if not chunk:
                        break
                    yield chunk
                process.wait()
            finally:
                if process.poll() is None:
                    process.kill()
        
        return StreamingResponse(stream_generator(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
