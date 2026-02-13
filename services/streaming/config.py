from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    minio_endpoint: str = "minio:9000"
    minio_access_key: str
    minio_secret_key: str
    bucket_name: str = "music"

    library_api_url: str = "http://library:8000/songs/"
    database_url: str = ""

    class Config:
        env_file = ".env"

settings = Settings()