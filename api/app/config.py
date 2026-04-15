from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://liberloci:liberloci@db:5432/liberloci"
    google_books_api_key: str = ""
    cover_max_size: int = 900
    cover_jpeg_quality: int = 85

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
