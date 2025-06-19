from concurrent.futures import ThreadPoolExecutor
import logging
from fastapi import APIRouter, HTTPException, Query, logger
from models import SearchResult, AudioInfo
from typing import List
import asyncio
from services.youtube_service import(
    get_most_viewed_music,
    get_similar_videos,
    get_trending_music,
    get_video_info,
    get_search_result,
)

router = APIRouter()

#logger for logging errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#threads to execute functions asynchronously
executor = ThreadPoolExecutor(max_workers=4)

#Get method on /search with required query parameter and optional max results 
#for sending search videos to youtube API
@router.get('/search', response_model=List[SearchResult])
async def search_youtube(
    q: str = Query(..., description="Youtube search query")):
    try:
        search = await asyncio.get_event_loop().run_in_executor(
            executor, get_search_result, q
        )
        return search
         
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed {str(e)}")


#GET METHOD FOR GETTING YOUTUBE AUDIO URL
@router.get("/info/{video_id}", response_model=AudioInfo)
async def get_audio_info(video_id: str):
    try:
        info = await asyncio.get_event_loop().run_in_executor(
            executor, get_video_info, video_id
        )
        return info
    
    except Exception as e:
        logger.error(f"Stream Info error {str(e)}")
        raise HTTPException(status_code=404, detail="Video not found")
    
#GET METHOD FOR GETTING REALTED VIEDO TO THE MUSIC BEING PLAYED
@router.get("/recommendation/{video_id}", response_model=List[SearchResult])
async def music_recommendation(video_id: str):
    try:
        recommendation = await asyncio.get_event_loop().run_in_executor(
            executor, get_similar_videos, video_id
        )
        return recommendation
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error while recommending: {str(e)}")

@router.get("/trending", response_model=List[SearchResult])
async def trending_music():
    try:
        trending = await asyncio.get_event_loop().run_in_executor(
            executor, get_trending_music
        )
        return trending
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting trending: {str(e)}")
    

@router.get("/most_viewed_music", response_model=List[SearchResult])
async def most_viewed_music():
    try:
        popular_music = await asyncio.get_event_loop().run_in_executor(
            executor, get_most_viewed_music
        )
        return popular_music
    except Exception as e:
        logger.error(f"popular error {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting trending: {str(e)}")