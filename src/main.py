import logging
import io
import asyncio
import os
import scipy.io.wavfile as wavfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.tts_engine import TTSLoaderFactory
from src.llm_engine import OllamaClient
from src.audio_config import FFMPEG_PARAMS

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TTS-Server")

app = FastAPI()

model_type = os.getenv("TTS_MODEL_TYPE", "mms")
try:
    loader = TTSLoaderFactory.get_loader(model_type)
    logger.info(f"Loaded model: {model_type}")
except ValueError as e:
    logger.error(f"Failed to initialize TTS engine: {e}")
    raise RuntimeError(f"Failed to initialize TTS engine: {e}")

llm = OllamaClient()


class ChatRequest(BaseModel):
    prompt: str


class TTSRequest(BaseModel):
    text: str
    reference_audio: str = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tts")
async def tts(request: TTSRequest):
    return await generate_audio(request.text, request.reference_audio)


@app.post("/tts_direct")
async def tts_direct(request: TTSRequest):
    return await generate_audio(request.text, request.reference_audio)
class ChatRequest(BaseModel):
    prompt: str
    reference_audio: str = None
    reference_text: str = None

@app.post("/chat")
async def chat(request: ChatRequest):
    text_response = await llm.generate_text(request.prompt)
    return await generate_audio(
        text_response, request.reference_audio, request.reference_text
    )

async def generate_audio(
    text: str, reference_audio: str = None, reference_text: str = None
):
    try:
        logger.info(f"Generating audio for text: {text[:50]}...")
        audio = loader.generate(
            text, reference_audio=reference_audio, reference_text=reference_text
        )
        if audio.dtype == "float32":
            audio = (audio * 32767).astype("int16")

        wav_buffer = io.BytesIO()
        wavfile.write(wav_buffer, loader.sampling_rate, audio)
        wav_buffer.seek(0)
        wav_data = wav_buffer.read()

        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-y",
            "-i",
            "pipe:0",
            *FFMPEG_PARAMS,
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def stream_generator():
            try:
                process.stdin.write(wav_data)
                await process.stdin.drain()
                process.stdin.close()
                while True:
                    chunk = await process.stdout.read(4096)
                    if not chunk:
                        break
                    yield chunk

                stderr_data = await process.stderr.read()
                if stderr_data:
                    logger.debug(f"FFmpeg stderr: {stderr_data.decode()}")

                await process.wait()
            finally:
                if process.returncode is None:
                    logger.warning("Terminating hanging FFmpeg process")
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        process.kill()

        return StreamingResponse(stream_generator(), media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error during audio generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
