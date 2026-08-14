from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import inspect, text
from .config import Config
from .official_registry import ensure_registry_templates
from .time_utils import utc_now

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["300 per day", "60 per hour"])


def _sync_legacy_schema():
    """Tambahkan kolom autentikasi baru ke database lama tanpa migrasi manual."""
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return

    columns = {column['name'] for column in inspector.get_columns('users')}
    statements = []

    if 'full_name' not in columns:
        statements.append("ALTER TABLE users ADD COLUMN full_name VARCHAR(120) NOT NULL DEFAULT ''")
    if 'nis' not in columns:
        statements.append("ALTER TABLE users ADD COLUMN nis VARCHAR(32)")
    if 'nip' not in columns:
        statements.append("ALTER TABLE users ADD COLUMN nip VARCHAR(32)")

    for statement in statements:
        db.session.execute(text(statement))

    if statements:
        db.session.commit()

    db.session.execute(text(
        "UPDATE users SET full_name = username WHERE full_name IS NULL OR TRIM(full_name) = ''"
    ))
    db.session.execute(text(
        "UPDATE users SET nis = username WHERE role = 'mahasiswa' AND (nis IS NULL OR TRIM(nis) = '')"
    ))
    db.session.execute(text(
        "UPDATE users SET nip = username WHERE role = 'dosen' AND (nip IS NULL OR TRIM(nip) = '')"
    ))
    db.session.commit()


def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    ensure_registry_templates(app.config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'
    login_manager.login_message_category = 'warning'

    from .routes.auth import auth_bp
    from .routes.guru import guru_bp, dosen_bp
    from .routes.siswa import siswa_bp, mahasiswa_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(guru_bp)
    app.register_blueprint(dosen_bp)
    app.register_blueprint(siswa_bp)
    app.register_blueprint(mahasiswa_bp)

    @app.after_request
    def add_security_headers(response):
        """Tambahkan HTTP security headers ke setiap respons."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data:;"
        )
        return response

    @app.context_processor
    def inject_globals():
        return {'now': utc_now()}

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    with app.app_context():
        from . import models  # pastikan semua model terdaftar sebelum create_all
        db.create_all()
        _sync_legacy_schema()

    return app
