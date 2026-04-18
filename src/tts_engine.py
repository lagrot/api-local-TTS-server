import subprocess
import os

def generate_audio(text: str, output_path: str, bitrate: str = "128k"):
    """Genererar ljud via Piper binär och kodar till MP3 med FFmpeg."""
    raw_path = output_path.replace(".mp3", ".raw")
    
    # Kör piper
    cmd_piper = ["./bin/piper_bin", "--model", "models/piper/sv_SE-nst-medium.onnx", "--output-raw"]
    piper_proc = subprocess.run(cmd_piper, input=text.encode("utf-8"), capture_output=True, check=True)
    
    # Kör FFmpeg
    cmd_ffmpeg = [
        "ffmpeg", "-y", "-f", "s16le", "-ar", "22050", "-ac", "1", "-i", "pipe:0", 
        "-af", "compand=0.3|0.3:6:-70/-70|-60/-20|0/0:6:0:-90:0.2",
        "-codec:a", "libmp3lame", "-b:a", bitrate, output_path
    ]
    subprocess.run(cmd_ffmpeg, input=piper_proc.stdout, check=True, capture_output=True)
    
    if os.path.exists(raw_path):
        os.remove(raw_path)
    
    return output_path
