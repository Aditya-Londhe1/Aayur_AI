# backend/app/core/config.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PROJECT_NAME: str = "AayurAI"
    APP_NAME: str = "Aayur AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aayurai.db")
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:5173")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png")
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions as list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    # AI Models
    MODEL_DIR: str = os.getenv("MODEL_DIR", "./ml_models")
    USE_GPU: bool = os.getenv("USE_GPU", "False").lower() == "true"
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Multilingual
    DEFAULT_LOCALE: str = os.getenv("DEFAULT_LOCALE", "en")
    SUPPORTED_LOCALES: str = os.getenv("SUPPORTED_LOCALES", "en,hi,ta,te,kn,ml,bn,gu,mr,pa,ur")
    TRANSLATIONS_DIR: str = os.getenv("TRANSLATIONS_DIR", "./app/i18n/translations")
    
    @property
    def supported_locales_list(self) -> List[str]:
        """Parse supported locales as list"""
        return [locale.strip() for locale in self.SUPPORTED_LOCALES.split(",")]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@aayurai.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "AayurAI")
    
    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()