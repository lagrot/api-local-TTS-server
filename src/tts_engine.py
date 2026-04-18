import subprocess
import os
import logging

logger = logging.getLogger("tts-engine")

def generate_audio(text: str, output_path: str, bitrate: str = "128k"):
    """Genererar ljud via installerad piper och kodar till MP3."""
    # Använd 'piper' direkt (nu installerad i venv/bin)
    # Vi pekar ut modellen explicit
    piper_cmd = ["piper", "--model", "models/piper/sv_SE-nst-medium.onnx", "--output-raw"]
    
    try:
        # 1. Piper körs
        piper_proc = subprocess.run(piper_cmd, input=text.encode("utf-8"), capture_output=True, check=True)
        
        # 2. FFmpeg (med radio-kompressor)
        cmd_ffmpeg = [
            "ffmpeg", "-y", "-f", "s16le", "-ar", "22050", "-ac", "1", "-i", "pipe:0", 
            "-af", "compand=0.3|0.3:6:-70/-70|-60/-20|0/0:6:0:-90:0.2",
            "-codec:a", "libmp3lame", "-b:a", bitrate, output_path
        ]
        subprocess.run(cmd_ffmpeg, input=piper_proc.stdout, check=True, capture_output=True)
        
        logger.info(f"Audio generation complete: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"TTS/FFmpeg Error: {e.stderr.decode()}")
        raise RuntimeError("Pipeline Failed")
