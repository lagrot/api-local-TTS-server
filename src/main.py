import asyncio
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

# Dynamisk laddning av loader baserat på miljövariabel
model_type = os.getenv("TTS_MODEL_TYPE", "mms")
try:
    loader = TTSLoaderFactory.get_loader(model_type)
except ValueError as e:
    raise RuntimeError(f"Failed to initialize TTS engine: {e}")

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


import asyncio

# ... (rest of imports)

async def generate_audio(text: str):
    try:
        audio = loader.generate(text)

        if audio.dtype == "float32":
            audio = (audio * 32767).astype("int16")

        wav_buffer = io.BytesIO()
        sr = loader.sampling_rate
        wavfile.write(wav_buffer, sr, audio)
        wav_buffer.seek(0)
        wav_data = wav_buffer.read()

        # Asynkron FFmpeg-process
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-y",
            "-i", "pipe:0",
            "-f", "mp3",
            "-ab", "320k",
            "-ar", "48000",
            "-af", "aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6",
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def stream_generator():
            try:
                # Skicka data asynkront
                process.stdin.write(wav_data)
                await process.stdin.drain()
                process.stdin.close()

                # Läs output asynkront
                while True:
                    chunk = await process.stdout.read(4096)
                    if not chunk:
                        break
                    yield chunk
                await process.wait()
            finally:
                if process.returncode is None:
                    process.terminate()

        return StreamingResponse(stream_generator(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
