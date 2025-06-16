from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.youtube import router
import uvicorn
from services import auth_service
import os
import sys
from dotenv import load_dotenv

#load environemnt variable depending on if it is running for ececutable or no
if getattr(sys, 'frozen', False):
    # Running as bundled .exe
    dotenv_path = os.path.join(sys._MEIPASS, '.env')
else:
    # Running as script
    dotenv_path = '.env'

load_dotenv(dotenv_path)

app = FastAPI(title="SanBeats API")

#setting up middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(router, tags=["Youtube API"])
app.include_router(auth_service.router, tags=["Google Login"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)