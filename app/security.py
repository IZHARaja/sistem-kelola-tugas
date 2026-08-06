"""
Modul utilitas keamanan.
Menyediakan sanitasi input, logging audit, dan validasi password.
"""
import re
import bleach
from datetime import datetime
from flask import request
from . import db

_ALLOWED_TAGS: list = []      # Tidak ada tag HTML yang diizinkan
_ALLOWED_ATTRIBUTES: dict = {}


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Strip seluruh tag HTML dan batasi panjang string untuk mencegah XSS/stored injection."""
    if not isinstance(text, str):
        return ''
    clean = bleach.clean(text, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES, strip=True)
    return clean[:max_length].strip()


def log_security_event(event_type: str, username: str = None, details: str = None) -> None:
    """Catat event keamanan ke database untuk audit trail."""
    from .models import SecurityLog
    try:
        log = SecurityLog(
            event_type=(event_type or '')[:50],
            username=(username or '')[:64],
            ip_address=(request.remote_addr or '')[:45],
            user_agent=(request.headers.get('User-Agent', '') or '')[:250],
            details=(details or '')[:500],
            timestamp=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()


def validate_password_strength(password: str) -> tuple:
    """
    Validasi kekuatan password.
    Mengembalikan (is_valid: bool, pesan_error: str).
    """
    if len(password) < 8:
        return False, 'Password minimal 8 karakter.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password harus mengandung setidaknya satu huruf kapital (A-Z).'
    if not re.search(r'[a-z]', password):
        return False, 'Password harus mengandung setidaknya satu huruf kecil (a-z).'
    if not re.search(r'\d', password):
        return False, 'Password harus mengandung setidaknya satu angka (0-9).'
    return True, ''
