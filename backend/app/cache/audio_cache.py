import datetime
import time
import yt_dlp

from models.results_models import AudioInfo
from services.format_service import format_duration

#variable for in-memory cache
cached_info: dict[str, dict] = {}

#cache for 6hrs max as yt-dlp link expires in 6 hrs
CACHE_DURATION = 6*3600

def is_valid(entry: dict) -> bool:
    return time.time() < entry.get("expires_at", 0)

def get_cached_audio_info(video_id: str) -> AudioInfo:
    entry = cached_info.get(video_id)
    return entry if entry and is_valid(entry) else None

def extract_audio_url_and_info(video_id) -> AudioInfo:
    global cached_info #store in global variable
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
    
    audio_info = {
        "url": info['url'],
        "title": info.get('title', ''),
        "thumbnail": info.get('thumbnail', ''),
        "channel":info.get('channel', 'Unknown Channel'),
        "expires_at":time.time() + CACHE_DURATION,
        "duration": formatted_duration,
        "format": "m4a",
        "quality": '128kbps',
    }
    cached_info[video_id] = audio_info
    return audio_info
