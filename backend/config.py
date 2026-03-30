import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "medimart")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_EXPIRES_DAYS = int(os.getenv("JWT_EXPIRES_DAYS", "300"))

ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "15"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")
RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "10 per minute")
RATE_LIMIT_ORDER = os.getenv("RATE_LIMIT_ORDER", "30 per minute")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
