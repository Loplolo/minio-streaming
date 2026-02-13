import os
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from minio import Minio
from .config import settings  

app = FastAPI()

minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False
)

    
@app.post("/upload")
async def upload_song(
    file: UploadFile, 
    title: str = Form(...),  
    artist: str = Form(...),
    album: str = Form(...),
    genre: str = Form(...),
):

    found = minio_client.bucket_exists(settings.bucket_name)
    if not found:
        minio_client.make_bucket(settings.bucket_name)

    try:
        minio_client.put_object(
            settings.bucket_name, 
            file.filename, 
            file.file, 
            length=-1, 
            part_size=10*1024*1024
        )

        song_data = {
            "title": title,
            "artist": artist,
            "album": album,
            "genre": genre,
            "filename": file.filename,
        }
        
        response = requests.post(settings.library_api_url, params=song_data)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Library service failed to store metadata")

        return {"message": f"File {file.filename} uploaded and metadata stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{filename}")
async def delete_song(filename: str):
    try:
        minio_client.remove_object(settings.bucket_name, filename)

        response = requests.delete(f"{settings.library_api_url}filename/{filename}")

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Library service failed to delete metadata")

        return {"message": f"File {filename} deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))