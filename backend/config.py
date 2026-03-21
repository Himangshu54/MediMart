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

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
