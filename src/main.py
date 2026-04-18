import torch
import io
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.tts_engine import MMSLoader
import scipy.io.wavfile as wavfile

app = FastAPI()
loader = MMSLoader()

class TTSRequest(BaseModel):
    text: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/tts")
async def tts(request: TTSRequest):
    try:
        inputs = loader.tokenizer(request.text, return_tensors="pt")
        with torch.no_grad():
            output = loader.model(**inputs)
        
        audio = output.waveform[0].numpy()
        
        # Spara till RAM-buffer
        wav_buffer = io.BytesIO()
        wavfile.write(wav_buffer, loader.model.config.sampling_rate, audio)
        wav_buffer.seek(0)
        
        # Konvertera till högkvalitativ MP3 med FFmpeg-filter för radio-feeling
        process = subprocess.Popen(
            [
                'ffmpeg', '-y', '-i', 'pipe:0', 
                '-f', 'mp3', 
                '-ab', '320k',              # Max bitrate
                '-ar', '48000',             # 48kHz (TV-standard)
                '-af', 'aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6', 
                'pipe:1'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mp3_data, _ = process.communicate(input=wav_buffer.read())
        
        return StreamingResponse(io.BytesIO(mp3_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
