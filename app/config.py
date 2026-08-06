import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Config:
    # SECURITY: Tetapkan SECRET_KEY di .env untuk produksi.
    # Jika tidak di-set, key acak di-generate setiap restart (invalidasi semua sesi).
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tugasapp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # Token CSRF expired setelah 1 jam

    SESSION_COOKIE_HTTPONLY = True   # Cegah akses JS ke cookie sesi
    SESSION_COOKIE_SAMESITE = 'Lax'  # Mitigasi CSRF lintas-situs
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # HTTPS only di produksi
    PERMANENT_SESSION_LIFETIME = 1800  # Sesi kedaluwarsa setelah 30 menit idle

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Batas upload 16 MB

    UPLOAD_FOLDER = 'instance/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg', 'ppt', 'pptx', 'xlsx', 'xls'}
