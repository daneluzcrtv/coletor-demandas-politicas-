from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    anthropic_api_key: str
    nominatim_user_agent: str = "coletor-demandas/1.0"

    # Meta WhatsApp Cloud API
    whatsapp_phone_number_id: str
    whatsapp_access_token: str
    whatsapp_verify_token: str

    # Auth
    jwt_secret: str = "troque-em-producao"

    class Config:
        env_file = ".env"


settings = Settings()
