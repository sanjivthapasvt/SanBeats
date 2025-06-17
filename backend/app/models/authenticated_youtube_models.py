from pydantic import BaseModel
from typing import List, Optional

class Thumbnail(BaseModel):
    url: str

class Thumbnails(BaseModel):
    default: Optional[Thumbnail]
    medium: Optional[Thumbnail]
    high: Optional[Thumbnail]

class PlayListItem(BaseModel):
    id: str
    title: str
    thumbnails: Thumbnails
    channelTitle: str

class YoutubePlaylistResponse(BaseModel):
    nextPageToken: Optional[str] = None
    items: List[PlayListItem]
    