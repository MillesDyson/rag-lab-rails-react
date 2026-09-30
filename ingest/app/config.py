from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# fora do container o .env fica na raiz do monorepo, um nivel acima de ingest/;
# dentro do container as variaveis chegam pelo env_file do compose
ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV if ROOT_ENV.exists() else None,
        extra="ignore",
    )

    openai_api_key: str = ""
    llama_cloud_api_key: str = ""

    pinecone_api_key: str = "pclocal"
    pinecone_host: str = "http://localhost:5080"
    pinecone_index: str = "raglab"

    rails_callback_url: str = "http://localhost:3000"
    internal_token: str = "dev-token-trocar-depois"

    # text-embedding-3-small -> 1536 dimensoes
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    vision_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"

    chunk_size: int = 1000
    chunk_overlap: int = 150


@lru_cache
def settings() -> Settings:
    return Settings()
