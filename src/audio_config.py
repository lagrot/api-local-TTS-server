# Radio Quality Audio Settings
FFMPEG_PARAMS = [
    "-f", "mp3",
    "-ab", "320k",
    "-ar", "48000",
    "-af", "aresample=48000:resampler=soxr,compand=attacks=0.01:points=-80/-900|-45/-15|-27/-9|0/-7|20/-5:gain=6",
]
