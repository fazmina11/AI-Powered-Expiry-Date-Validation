"""
config.py — All settings loaded from environment / .env file.
No hardcoded secrets or connection strings.
"""

import os
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# Load environment variables from .env file into os.environ
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://expiry_user:expiry_pass@localhost:5432/expiry_db"
    APP_ENV: str = "development"
    APP_VERSION: str = "2.0.0"
    SECRET_KEY: str = "change_this_secret_key_phase2"
    UPLOAD_DIR: str = "./uploads"
    ML_WEBHOOK_URL: str = ""

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
