"""
AI Tech Consultant - Meeting to Scope
Configuration management using Pydantic Settings.
"""
from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings for Meeting to Scope."""

    # API Keys
    anthropic_api_key: str = Field(default="", description="Anthropic API key for Claude")

    # Server Configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)

    # Consultant Defaults
    default_hourly_rate: float = Field(default=150.0, description="Standard consulting rate ($/hr)")
    consultant_name: str = Field(default="AI Tech Consultant", description="Consultant / Agency Name")
    platform_name: str = Field(default="Brilliant Directories", description="Target platform ecosystem")

    # Knowledge Brain Integration
    knowledge_brain_url: str = Field(default="http://localhost:8000")

    # Claude Models
    claude_model: str = Field(default="claude-sonnet-4-20250514", description="Primary model for scoping generation")
    claude_fast_model: str = Field(default="claude-haiku-4-20250514", description="Fast model for extraction")

    # Environment
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton loading from root .env if present."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        os.environ.setdefault("ENV_FILE", str(env_path))
    return Settings(_env_file=str(env_path) if env_path.exists() else ".env")
