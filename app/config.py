import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# Deteksi environment Vercel (filesystem read-only kecuali /tmp)
_on_vercel = bool(os.environ.get('VERCEL'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        ('sqlite:////tmp/tugasapp.db' if _on_vercel else 'sqlite:///tugasapp.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = _on_vercel or os.environ.get('FLASK_ENV') == 'production'
    PERMANENT_SESSION_LIFETIME = 1800

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Vercel hanya /tmp yang writable; lokal pakai instance/uploads
    UPLOAD_FOLDER = '/tmp/uploads' if _on_vercel else 'instance/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg', 'ppt', 'pptx', 'xlsx', 'xls'}
