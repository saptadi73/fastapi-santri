from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # ===== App Settings =====
    app_name: str = Field(default="Pendataan Santri API", alias="APP_NAME")
    secret_key: str = Field(default="default-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(default="postgresql://localhost/santri_db", alias="DATABASE_URL")

    # ===== OpenAI / LLM =====
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.3, alias="OPENAI_TEMPERATURE")

    # ===== Gemini AI =====
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.4, alias="GEMINI_TEMPERATURE")

    # ===== NL2SQL =====
    nl2sql_max_tokens: int = Field(default=2000, alias="NL2SQL_MAX_TOKENS")
    nl2sql_timeout_seconds: int = Field(default=30, alias="NL2SQL_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        populate_by_name=True
    )


settings = Settings()
