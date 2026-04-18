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
        inputs = loader.tokenizer(text, return_tensors="pt").to(loader.device)
        with torch.no_grad():
            output = loader.model(**inputs)
        
        audio = output.waveform[0].cpu().numpy()
        
        wav_buffer = io.BytesIO()
        wavfile.write(wav_buffer, loader.model.config.sampling_rate, audio)
        wav_buffer.seek(0)
        
        process = subprocess.Popen(
            ['ffmpeg', '-y', '-i', 'pipe:0', '-f', 'mp3', '-ab', '320k', '-ar', '48000', '-af', 'aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6', 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        # Write input to ffmpeg in a thread or non-blocking way if possible, 
        # but for now keep it simple and stream output.
        def stream_generator():
            try:
                # Write initial data to stdin
                process.stdin.write(wav_buffer.read())
                process.stdin.close()
                
                # Stream output chunks
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
