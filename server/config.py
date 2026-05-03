from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AGL_")

    database_url: str = "sqlite:///./data/agent_growth_layer.db"
    seed_skills_dir: Path = Field(default=Path("./templates/seed_skills"))
    llm_provider: str = "deterministic"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: float = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
