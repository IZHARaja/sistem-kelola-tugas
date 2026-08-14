import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .. import db, limiter
from ..models import User
from ..forms import LoginForm, RegisterForm
from ..official_registry import validate_official_registry
from ..security import log_security_event, validate_password_strength, sanitize_input

auth_bp = Blueprint('auth', __name__)

ROLE_LABELS = {
    'mahasiswa': 'siswa',
    'dosen': 'guru',
}


def _normalize_name(value):
    return ' '.join(sanitize_input(value or '', 120).split())


def _normalize_email(value):
    return sanitize_input(value or '', 120).strip().lower()


def _normalize_identifier(value):
    return ''.join(sanitize_input(value or '', 32).split()).upper()


def _build_username(role, identifier):
    base = f"{role}-{identifier.lower()}"[:64]
    candidate = base
    suffix = 1

    while User.query.filter_by(username=candidate).first():
        tail = f"-{suffix}"
        candidate = f"{base[:64 - len(tail)]}{tail}"
        suffix += 1

    return candidate


def _normalize_role(value, default='mahasiswa'):
    if value == 'dosen':
        return 'dosen'
    if value == 'mahasiswa':
        return 'mahasiswa'
    return default


def _build_auth_context(page, role_mode):
    role_mode = _normalize_role(role_mode)
    specific_endpoint = request.endpoint or f'auth.{page}'
    next_page = request.args.get('next', '')
    form_action = url_for(specific_endpoint, next=next_page) if page == 'login' and next_page else url_for(specific_endpoint)
    login_routes = {
        'mahasiswa': url_for('auth.login_mahasiswa', next=next_page) if next_page else url_for('auth.login_mahasiswa'),
        'dosen': url_for('auth.login_dosen', next=next_page) if next_page else url_for('auth.login_dosen'),
    }

    return {
        'role_mode': role_mode,
        'form_action': form_action,
        'login_routes': login_routes,
        'register_routes': {
            'mahasiswa': url_for('auth.register_mahasiswa'),
            'dosen': url_for('auth.register_dosen'),
        },
        'role_label': ROLE_LABELS[role_mode],
    }


def _build_portal_context():
    next_page = request.args.get('next', '')
    return {
        'login_routes': {
            'mahasiswa': url_for('auth.login_mahasiswa', next=next_page) if next_page else url_for('auth.login_mahasiswa'),
            'dosen': url_for('auth.login_dosen', next=next_page) if next_page else url_for('auth.login_dosen'),
        },
        'register_routes': {
            'mahasiswa': url_for('auth.register_mahasiswa'),
            'dosen': url_for('auth.register_dosen'),
        },
    }


def _set_role_default(form, role_mode, lock_role=False):
    if request.method == 'GET' or lock_role:
        form.role.data = role_mode


def _login_impl(role_mode=None):
    role_mode = _normalize_role(role_mode)
    locked_role = request.endpoint in ('auth.login_mahasiswa', 'auth.login_dosen')
    if current_user.is_authenticated:
        return _redirect_by_role()

    form = LoginForm()
    _set_role_default(form, role_mode, lock_role=locked_role)

    if form.validate_on_submit():
        safe_role = role_mode if locked_role else _normalize_role(form.role.data, None)
        safe_identifier = _normalize_identifier(form.identifier.data)
        safe_email = _normalize_email(form.email.data)
        safe_full_name = _normalize_name(form.full_name.data)

        user = None
        if safe_role == 'mahasiswa':
            user = User.query.filter_by(role='mahasiswa', nis=safe_identifier, email=safe_email).first()
        elif safe_role == 'dosen':
            user = User.query.filter_by(role='dosen', nip=safe_identifier, email=safe_email).first()

        full_name_matches = user and _normalize_name(user.full_name).casefold() == safe_full_name.casefold()

        if full_name_matches and user.is_active and user.check_password(form.password.data):
            login_user(user)
            log_security_event('LOGIN_SUCCESS', username=user.username)

            next_page = request.args.get('next', '')
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                return redirect(next_page)
            return _redirect_by_role()

        log_security_event('LOGIN_FAIL', username=safe_identifier,
                            details='Kredensial tidak valid')
        flash('Data login atau password salah.', 'danger')

    return render_template('auth/login.html', form=form, **_build_auth_context('login', role_mode))


def _register_impl(role_mode=None):
    role_mode = _normalize_role(role_mode)
    locked_role = request.endpoint in ('auth.register_mahasiswa', 'auth.register_dosen')
    if current_user.is_authenticated:
        return _redirect_by_role()

    form = RegisterForm()
    _set_role_default(form, role_mode, lock_role=locked_role)

    if form.validate_on_submit():
        is_valid, msg = validate_password_strength(form.password.data)
        if not is_valid:
            flash(msg, 'danger')
            return render_template('auth/register.html', form=form, **_build_auth_context('register', role_mode))

        allowed_roles = ('mahasiswa', 'dosen')
        safe_role = role_mode if locked_role else (form.role.data if form.role.data in allowed_roles else 'mahasiswa')
        safe_identifier = _normalize_identifier(form.nis.data if safe_role == 'mahasiswa' else form.nip.data)
        safe_email = _normalize_email(form.email.data)
        safe_full_name = _normalize_name(form.full_name.data)

        is_registered, message = validate_official_registry(
            current_app.config,
            safe_role,
            safe_identifier,
            safe_email,
            safe_full_name,
        )
        if not is_registered:
            flash(message, 'danger')
            return render_template('auth/register.html', form=form, **_build_auth_context('register', role_mode))

        user = User(
            username=_build_username(safe_role, safe_identifier),
            full_name=safe_full_name,
            email=safe_email,
            role=safe_role,
            nis=safe_identifier if safe_role == 'mahasiswa' else None,
            nip=safe_identifier if safe_role == 'dosen' else None,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_security_event('REGISTER_SUCCESS', username=user.username)
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login_mahasiswa' if safe_role == 'mahasiswa' else 'auth.login_dosen'))

    return render_template('auth/register.html', form=form, **_build_auth_context('register', role_mode))


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return _redirect_by_role()
    return render_template('auth/portal_select.html', **_build_portal_context())


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    return _login_impl(request.args.get('role', 'mahasiswa'))


@auth_bp.route('/login/siswa', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login_mahasiswa():
    return _login_impl('mahasiswa')


@auth_bp.route('/login/guru', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login_dosen():
    return _login_impl('dosen')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    return _register_impl(request.args.get('role', 'mahasiswa'))


@auth_bp.route('/register/siswa', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register_mahasiswa():
    return _register_impl('mahasiswa')


@auth_bp.route('/register/guru', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register_dosen():
    return _register_impl('dosen')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return _redirect_by_role()


@auth_bp.route('/logout')
@login_required
def logout():
    log_security_event('LOGOUT', username=current_user.username)
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/uploads/<path:filename>')
@login_required
def download_file(filename):
    """Layani file submission — hanya untuk user yang sudah login."""
    safe_name = os.path.basename(filename)  # cegah path traversal
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, safe_name, as_attachment=True)


def _redirect_by_role():
    """Arahkan user ke dashboard sesuai role-nya."""
    if current_user.role == 'dosen':
        return redirect(url_for('guru.dashboard'))
    return redirect(url_for('siswa.dashboard'))
