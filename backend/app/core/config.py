"""Application configuration using pydantic-settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings, loaded from environment variables."""

    # API
    api_title: str = "VERICLAIM API"
    api_description: str = "Scientific Claim & Citation Verification System"
    api_version: str = "1.0.0"

    # Models
    embedding_model: str = "all-MiniLM-L6-v2"
    nli_model: str = "cross-encoder/nli-MiniLM2-L6-H768"
    claim_model: str = "typeform/distilbert-base-uncased-mnli"

    # Thresholds
    claim_detection_threshold: float = 0.15
    similarity_threshold: float = 0.3
    high_confidence_threshold: float = 0.75
    low_confidence_threshold: float = 0.4

    # Retrieval
    top_k: int = 3
    embedding_dimension: int = 384

    # File handling
    max_file_size_mb: int = 50
    upload_dir: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../data/raw")
    )

    # Model cache
    model_cache_dir: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../models")
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Force HuggingFace to use the project's models directory on the D drive
os.environ["HF_HOME"] = settings.model_cache_dir
os.environ["TRANSFORMERS_CACHE"] = settings.model_cache_dir
