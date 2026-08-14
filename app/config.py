import os
import secrets
from dotenv import load_dotenv

load_dotenv()

# Deteksi environment Vercel (filesystem read-only kecuali /tmp)
_on_vercel = bool(os.environ.get('VERCEL'))
_local_sqlite_name = os.environ.get('SQLITE_DB_NAME', 'sikeltugas.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    OFFICIAL_DATA_FOLDER = os.environ.get('OFFICIAL_DATA_FOLDER') or os.path.join('instance', 'official_data')
    SISWA_REGISTRY_FILE = os.environ.get('SISWA_REGISTRY_FILE') or os.path.join(OFFICIAL_DATA_FOLDER, 'siswa_resmi.xlsx')
    GURU_REGISTRY_FILE = os.environ.get('GURU_REGISTRY_FILE') or os.path.join(OFFICIAL_DATA_FOLDER, 'guru_resmi.xlsx')

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        ('sqlite:////tmp/tugasapp.db' if _on_vercel else f'sqlite:///{_local_sqlite_name}')
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
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt', 'zip',
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp',
        'ppt', 'pptx', 'xlsx', 'xls'
    }
