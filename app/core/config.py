import os
from sqlalchemy.engine.url import URL, make_url

SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

DATABASE_URL: str | URL = make_url(
    os.getenv("DATABASE_URL", "postgresql+asyncpg://app:app@db:5432/fastapi")
)

GIT_SHA: str = os.getenv("GIT_SHA", "unknown")

# CORS Configuration - restrictive origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",  # Frontend in Docker
    "http://localhost:8080",
    "https://yourdomain.com",
]

CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
if CORS_ORIGINS_ENV:
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",")]
