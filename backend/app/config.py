import os
from pathlib import Path

# Carrega .env local se existir (desenvolvimento)
env_file = Path(".env")
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)


class Settings:
    database_url: str              = os.environ.get("DATABASE_URL", "")
    anthropic_api_key: str         = os.environ.get("ANTHROPIC_API_KEY", "")
    nominatim_user_agent: str      = os.environ.get("NOMINATIM_USER_AGENT", "coletor-demandas/1.0")
    whatsapp_phone_number_id: str  = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "placeholder")
    whatsapp_access_token: str     = os.environ.get("WHATSAPP_ACCESS_TOKEN", "placeholder")
    whatsapp_verify_token: str     = os.environ.get("WHATSAPP_VERIFY_TOKEN", "placeholder")
    jwt_secret: str                = os.environ.get("JWT_SECRET", "troque-em-producao")


settings = Settings()
