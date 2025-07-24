from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    # Scheduler lambda values
    lambda_trend: float = 0.3
    lambda_sim: float = 0.2
    lambda_depth: float = 0.05
    
    # OpenAI settings
    openai_api_key: str = ""
    persona_model: str = "gpt-4o-mini"
    critic_model: str = "gpt-4o-mini"
    mutator_model: str = "gpt-4o-mini"
    daily_budget_usd: float = 2.00

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
