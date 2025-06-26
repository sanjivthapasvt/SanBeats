import os
from yt_dlp import YoutubeDL

def download_youtube_video(path: str, video_url: str, video: bool = True, quality: int = None):
    path = os.path.expanduser(path)
    os.makedirs(path, exist_ok=True)

    # Base options
    ydl_opts = {
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
        'keep_video': True
    }

    if video:
        # if video is true in parameter and qualit is given it download based on that else default
        if quality:
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
        else:
            ydl_opts['format'] = 'best'
        
    else:
        # if the video in parameter is false it will download audio only in mp3
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    # Start downloading
    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"{'Video' if video else 'Audio'} download started for: {video_url}")
            ydl.download([video_url])
            return True
        except Exception as e:
            print(f"Error while downloading: {e}")
            return False
