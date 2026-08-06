from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
import os
from .. import db, limiter
from ..models import User
from ..forms import LoginForm, RegisterForm
from ..security import log_security_event, validate_password_strength, sanitize_input

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return _redirect_by_role()

    form = LoginForm()
    if form.validate_on_submit():
        safe_username = sanitize_input(form.username.data, 64)
        # ORM query dengan parameterized binding — mencegah SQL Injection (OWASP A03)
        user = User.query.filter_by(username=safe_username).first()

        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            log_security_event('LOGIN_SUCCESS', username=user.username)

            # Mitigasi Open Redirect: hanya izinkan path relatif tanpa "//" di awal
            next_page = request.args.get('next', '')
            if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                return redirect(next_page)
            return _redirect_by_role()
        else:
            log_security_event('LOGIN_FAIL', username=safe_username,
                                details='Kredensial tidak valid')
            # Pesan generik — tidak bocorkan info apakah username ada atau tidak
            flash('Username atau password salah.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return _redirect_by_role()

    form = RegisterForm()
    if form.validate_on_submit():
        is_valid, msg = validate_password_strength(form.password.data)
        if not is_valid:
            flash(msg, 'danger')
            return render_template('auth/register.html', form=form)

        # Whitelist validasi role — mencegah privilege escalation
        allowed_roles = ('mahasiswa', 'dosen')
        safe_role = form.role.data if form.role.data in allowed_roles else 'mahasiswa'

        user = User(
            username=sanitize_input(form.username.data, 64),
            email=sanitize_input(form.email.data, 120),
            role=safe_role,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        log_security_event('REGISTER_SUCCESS', username=user.username)
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


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
        return redirect(url_for('dosen.dashboard'))
    return redirect(url_for('mahasiswa.dashboard'))
