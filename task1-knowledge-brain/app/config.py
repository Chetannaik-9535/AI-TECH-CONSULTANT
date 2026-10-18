"""
AI Tech Consultant - Knowledge Brain
Configuration management using Pydantic Settings.
"""
from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # API Keys
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude")
    openai_api_key: str = Field(default="", description="OpenAI API key for embeddings")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Sitemap & Crawling
    sitemap_url: str = Field(
        default="https://support.brilliantdirectories.com/support/sitemap.xml"
    )
    crawl_delay_seconds: float = Field(default=2.0, description="Delay between requests")
    crawl_concurrency: int = Field(default=3, description="Max concurrent requests")
    crawl_batch_size: int = Field(default=10, description="Pages per batch")
    crawl_max_retries: int = Field(default=3)
    crawl_user_agent: str = Field(
        default="AITechConsultant-KnowledgeBrain/1.0 (Educational Project)"
    )

    # Database
    database_url: str = Field(default="sqlite:///./ai_tech_consultant.db")
    chroma_persist_dir: str = Field(default="./chroma_db")

    # Models
    claude_model: str = Field(default="claude-sonnet-4-20250514", description="Primary Claude model")
    claude_haiku_model: str = Field(default="claude-haiku-4-20250514", description="Fast Claude model")
    embedding_model: str = Field(default="text-embedding-3-small")

    # RAG
    chunk_size: int = Field(default=800, description="Target chunk size in tokens")
    chunk_overlap: int = Field(default=100, description="Overlap between chunks")
    retrieval_top_k: int = Field(default=5, description="Number of chunks to retrieve")
    min_relevance_score: float = Field(default=0.3, description="Minimum similarity score")

    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    image_cache_dir: Path = Field(default_factory=lambda: Path("./image_cache"))
    data_dir: Path = Field(default_factory=lambda: Path("./data"))

    # Logging
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    # Try loading .env from project root
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        os.environ.setdefault("ENV_FILE", str(env_path))
    return Settings(_env_file=str(env_path) if env_path.exists() else ".env")
