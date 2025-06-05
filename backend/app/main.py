import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import youtube
import uvicorn
app = FastAPI(title="SanBeats API")

#Get api key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

#setting up middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(youtube.router, tags=["Youtube API"])

uvicorn.run(app, host="127.0.0.1", port=8000)