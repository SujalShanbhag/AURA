from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATABASE_URL: str

    REDIS_URL: str

    JWT_SECRET: str

    OPENAI_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

    ANTHROPIC_API_KEY: str = ""

    QDRANT_URL: str

    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()