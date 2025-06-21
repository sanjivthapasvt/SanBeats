import datetime
import subprocess
import time
import yt_dlp

from models.results_models import AudioInfo
from services.youtube_service import format_duration

#variable for in-memory cache
audio_url_cache = {}

#cache for 6hrs max as yt-dlp link expires in 6 hrs
CACHE_DURATION = 6*3600

def is_valid(entry):
    return time.time() < entry["expires_at"]

def get_cached_audio_url(video_id):
    entry = audio_url_cache.get(video_id)
    if entry and is_valid(entry):
        return entry["audio_url"]
    return None

def extract_audio_url_and_info(video_id):
    url = subprocess.check_output([
        "yt-dlp", "-f", "bestaudio", "--get-url",
        f"https://youtube.com/watch?v={video_id}"
    ]).decode().strip()
    
    audio_url_cache[video_id] = {
        "audio_url": url,
        "expires_at": time.time() + CACHE_DURATION
    }
    return url

def get_video_info(video_id: str) -> AudioInfo:
    ydl_opts = {
        'quiet': True,
        'format': '140',
        'noplaylist': True,
        'socket_timeout': 5,
        'retries': 0,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)
        
        duration_seconds = info.get('duration', 0)
        formatted_duration = format_duration(datetime.timedelta(seconds=duration_seconds))
        
        return AudioInfo(
            url=info['url'],
            title=info.get('title', ''),
            duration=formatted_duration,
            format='m4a',
            quality='128kbps',
            thumbnail=info.get('thumbnail', ''),
        )
        