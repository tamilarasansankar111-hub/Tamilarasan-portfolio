"""
Application configuration.
All secrets are loaded from environment variables (see .env.example).
Never hardcode real keys here.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours

    # Supabase
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")  # server-side only, bypasses RLS
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")        # used only for Auth sign-in calls

    # Admin
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "tamilarasansankar111@gmail.com")

    # Storage buckets
    BUCKET_PROFILE_PHOTOS = "profile-photos"
    BUCKET_RESUMES = "resumes"
    BUCKET_PROJECT_IMAGES = "project-images"
    BUCKET_CERTIFICATE_IMAGES = "certificate-images"

    # Upload limits
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15 MB per request
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
