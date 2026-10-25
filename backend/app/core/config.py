"""Application configuration loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Green Campus Sustainability Auditor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database — SQLite for local dev, Neon PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./green_campus.db"

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    # Comma-separated allowed frontend origins.
    # Local:      http://localhost:5173
    # Production: https://green-campus-frontend.onrender.com
    # Render auto-injects a single URL via the render.yaml fromService binding.
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "uploads"

    DEFAULT_EMISSION_FACTOR: float = 0.716  # kgCO2e/kWh - CEA India 2022-23
    EMISSION_FACTOR_SOURCE: str = "CEA CO2 Baseline Database Version 18 (2022-23)"
    EMISSION_FACTOR_UNIT: str = "kgCO2e/kWh"

    # Google Gemini Free API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_ENABLED: bool = False

    # Legacy Ollama settings (kept for backwards compat but not used)
    OLLAMA_BASE_URL: str = ""
    OLLAMA_MODEL: str = ""
    OLLAMA_ENABLED: bool = False

    DEMO_SEED: int = 42
    DEMO_CAMPUS_NAME: str = "Green Valley University (Demo)"

    @property
    def allowed_origins(self) -> list[str]:
        """Parse FRONTEND_ORIGIN — supports comma-separated list and wildcards."""
        origins = [o.strip() for o in self.FRONTEND_ORIGIN.split(",") if o.strip()]
        # Always allow localhost for dev convenience
        if "http://localhost:5173" not in origins:
            origins.append("http://localhost:5173")
        if "http://127.0.0.1:5173" not in origins:
            origins.append("http://127.0.0.1:5173")
        return origins


settings = Settings()

