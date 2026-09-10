import os
import sys
from pathlib import Path

# Carrega .env local se existir (desenvolvimento)
env_file = Path(".env")
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Debug temporário — remover após resolver
print("=== DEBUG ENV ===", file=sys.stderr, flush=True)
print(f"DATABASE_URL presente: {'DATABASE_URL' in os.environ}", file=sys.stderr, flush=True)
print(f"ANTHROPIC_API_KEY presente: {'ANTHROPIC_API_KEY' in os.environ}", file=sys.stderr, flush=True)
print(f"Total vars: {len(os.environ)}", file=sys.stderr, flush=True)
print(f"Vars com DATABASE: {[k for k in os.environ if 'DATABASE' in k.upper()]}", file=sys.stderr, flush=True)
print("=== END DEBUG ===", file=sys.stderr, flush=True)


class Settings:
    database_url: str              = os.environ.get("DATABASE_URL", "")
    anthropic_api_key: str         = os.environ.get("ANTHROPIC_API_KEY", "")
    nominatim_user_agent: str      = os.environ.get("NOMINATIM_USER_AGENT", "coletor-demandas/1.0")
    whatsapp_phone_number_id: str  = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "placeholder")
    whatsapp_access_token: str     = os.environ.get("WHATSAPP_ACCESS_TOKEN", "placeholder")
    whatsapp_verify_token: str     = os.environ.get("WHATSAPP_VERIFY_TOKEN", "placeholder")
    jwt_secret: str                = os.environ.get("JWT_SECRET", "troque-em-producao")


settings = Settings()
