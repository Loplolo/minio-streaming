import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

app = FastAPI()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    filename = Column(String) # song.mp3

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/songs/")
def create_song(title: str, artist: str, album: str, genre: str, filename: str,  db: Session = Depends(get_db)):
    new_song = Song(title=title, artist=artist, album=album, genre=genre, filename=filename)
    try:
        db.add(new_song)
        db.commit()
        db.refresh(new_song)
        return {"message": f"Song '{filename}' added successfully", "id": new_song.id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/songs/")
def read_songs(db: Session = Depends(get_db)):
    try:    
        return db.query(Song).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/songs/id/{song_id}")
def return_song_by_id(song_id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if song:
        return song
    else:
        raise HTTPException(status_code=404, detail=f"Song with id {song_id} not found")

@app.get("/songs/{filename}")   
def return_song_id_by_filename(filename: str, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.filename == filename).first()
    if song:
        return {"id": song.id}
    else:
        raise HTTPException(status_code=404, detail=f"Song with filename {filename} not found")
    

@app.delete("/songs/id/{song_id}")
def delete_song_by_id(song_id: int, db: Session = Depends(get_db)):
    
    song = db.query(Song).filter(Song.id == song_id).first()

    if song:
        db.delete(song)
        db.commit()
        return {"message": f"Song with id {song_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Song with id {song_id} not found")

@app.delete("/songs/filename/{filename}")
def delete_song_by_filename(filename: str, db: Session = Depends(get_db)):
    
    song = db.query(Song).filter(Song.filename == filename).first()

    if song:
        db.delete(song)
        db.commit()
        return {"message": f"Song {filename} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Song {filename} not found")