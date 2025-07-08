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


def extract_audio_url_and_info(video_id) -> dict:
    global cached_info #global variable

    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'noplaylist': True,
        'socket_timeout': 5,
        'retries': 0,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)
        except Exception as e:
            print(f"Error extracting info: {e}")
            raise Exception("Stream Info error")

        # Filter out unwanted m3u8/hls formats
        audio_formats = [
            f for f in info.get("formats", [])
            if f.get("ext") in ["m4a", "webm", "mp4"]
            and not f.get("protocol", "").startswith("m3u8")
            and not f.get("url", "").endswith(".m3u8")
        ]

        if not audio_formats:
            raise Exception("No suitable audio formats found")

        # pick best available audio format
        best_audio = max(audio_formats, key=lambda f: f.get("abr", 0) or 0)

        duration_seconds = info.get('duration', 0)
        formatted_duration = format_duration(datetime.timedelta(seconds=duration_seconds))

        audio_info = {
            "url": best_audio['url'],
            "title": info.get('title', ''),
            "thumbnail": info.get('thumbnail', ''),
            "channel": info.get('channel', 'Unknown Channel'),
            "expires_at": time.time() + CACHE_DURATION,
            "duration": formatted_duration,
            "format": best_audio.get("ext", "unknown"),
            "quality": f"{best_audio.get('abr', 'Unknown')}kbps",
        }

        cached_info[video_id] = audio_info
        return audio_info
