# config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    log_level: str = Field("INFO", env="IFC_READER_LOG_LEVEL")
    geometry: bool  = Field(True, env="IFC_READER_GEOM")

    class Config:
        env_file = ".env"

settings = Settings()
