from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str
    title: str
    duration: str
    thumbnail: str
    channel: str
    
class AudioInfo(BaseModel):
    url: str
    title: str
    duration: str
    format: str
    quality: str
    thumbnail: str
    channel: str
    expires_at: float
    
class AudioUrlAndInfo(BaseModel):
    video_id: AudioInfo