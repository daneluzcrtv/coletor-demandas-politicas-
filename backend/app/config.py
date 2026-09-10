from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    anthropic_api_key: str
    nominatim_user_agent: str = "coletor-demandas/1.0"

    # Meta WhatsApp Cloud API
    whatsapp_phone_number_id: str = "placeholder"
    whatsapp_access_token: str = "placeholder"
    whatsapp_verify_token: str = "placeholder"

    # Auth
    jwt_secret: str = "troque-em-producao"


settings = Settings()
