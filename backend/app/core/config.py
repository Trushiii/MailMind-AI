from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./mailmind.db"
    backend_cors_origins: str = "http://localhost:5173"
    
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = ""
    frontend_url: str = "http://localhost:5173"
    encryption_key: str = ""
    
    gemini_api_key: str = ""
    telegram_bot_token: str = ""

    morning_report_time: str = "08:00"
    evening_report_time: str = "20:00"
    timezone: str = "Asia/Colombo"

    # --- These were missing! ---
    vapid_public_key: str = ""
    vapid_private_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

settings = Settings()