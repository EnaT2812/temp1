"""
app/core/settings.py

Application settings and environment-based configuration.
All configuration values can be overridden via a .env file or environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Ollama / LLM ──────────────────────────────────────────────────────────
    # Local Ollama endpoint (default) – override with the public Pinggy URL
    # when running on Google Colab, e.g. http://<token>.a.free.pinggy.link
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL of the Ollama server (local or Pinggy tunnel).",
    )
    llm_model: str = Field(
        default="gpt-oss:20b",
        description="Ollama model tag used for response drafting.",
    )
    llm_timeout: int = Field(
        default=120,
        description="HTTP timeout (seconds) for LLM calls.",
    )

    # ── Intent model (Lab 2 fine-tuned checkpoint) ────────────────────────────
    # Point this to the local path or HuggingFace model-id of your fine-tuned
    # intent classifier from Lab 2.  The intent_node will load it from here.
    intent_model_path: str = Field(
        default="intent_model_checkpoint",
        description="Path or HuggingFace model-id for the fine-tuned intent classifier.",
    )

    # ── FastAPI server ─────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0", description="Host for the FastAPI server.")
    port: int = Field(default=8000, description="Port for the FastAPI server.")
    reload: bool = Field(default=True, description="Enable hot-reload for development.")

    # ── Misc ───────────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO", description="Logging level.")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton settings instance used throughout the application
settings = Settings()
