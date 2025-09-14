from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    INIT_DB: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
