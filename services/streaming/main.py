import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
import requests
from .config import settings 

app = FastAPI()

client = Minio(
    settings.minio_endpoint,            
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False
)


@app.get("/stream/{song_id}")
async def stream_by_id(song_id: int):
    
    url = f"{settings.library_api_url.rstrip('/')}/id/{song_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Song not found")

    song_info = response.json()
    filename = song_info['filename']
    
    minio_response = client.get_object(settings.bucket_name, filename)
    return StreamingResponse(minio_response, media_type="audio/mpeg")