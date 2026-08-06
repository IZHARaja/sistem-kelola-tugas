import os
import uuid
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .. import db
from ..models import Tugas, Submission
from ..forms import SubmissionForm
from ..security import sanitize_input, log_security_event


def _allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', set())


def _save_upload(file_obj):
    """Simpan file dengan nama unik, kembalikan (unique_name, original_name)."""
    original = secure_filename(file_obj.filename)
    unique_name = f"{uuid.uuid4().hex}_{original}"
    folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    file_obj.save(os.path.join(folder, unique_name))
    return unique_name, original

mahasiswa_bp = Blueprint('mahasiswa', __name__, url_prefix='/mahasiswa')


def mahasiswa_required(f):
    """Decorator: tolak akses jika bukan role mahasiswa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'mahasiswa':
            log_security_event(
                'ACCESS_DENIED',
                username=getattr(current_user, 'username', 'anonymous'),
                details=f'Akses tidak sah ke endpoint mahasiswa: {f.__name__}'
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated


@mahasiswa_bp.route('/dashboard')
@login_required
@mahasiswa_required
def dashboard():
    tugas_list = Tugas.query.order_by(Tugas.deadline.asc()).all()
    # Ambil ID tugas yang sudah disubmit secara efisien
    submitted_ids = {
        row.tugas_id for row in
        Submission.query.filter_by(mahasiswa_id=current_user.id)
        .with_entities(Submission.tugas_id).all()
    }
    pending_count = len(tugas_list) - len(submitted_ids)
    return render_template('mahasiswa/dashboard.html',
                           tugas_list=tugas_list,
                           submitted_ids=submitted_ids,
                           pending_count=pending_count)


@mahasiswa_bp.route('/tugas/<int:tugas_id>/submit', methods=['GET', 'POST'])
@login_required
@mahasiswa_required
def submit_tugas(tugas_id):
    tugas = Tugas.query.get_or_404(tugas_id)

    # Cek deadline sebelum proses lebih lanjut
    if datetime.utcnow() > tugas.deadline:
        flash('Deadline tugas sudah lewat. Tidak dapat mengumpulkan.', 'danger')
        return redirect(url_for('mahasiswa.dashboard'))

    # Cek duplikasi submission — mencegah double-submit & IDOR
    existing = Submission.query.filter_by(
        tugas_id=tugas_id,
        mahasiswa_id=current_user.id  # Selalu bind ke sesi aktif — mencegah IDOR
    ).first()

    if existing:
        flash('Anda sudah mengumpulkan tugas ini sebelumnya.', 'warning')
        return redirect(url_for('mahasiswa.dashboard'))

    form = SubmissionForm()
    if form.validate_on_submit():
        file_path = None
        file_original = None

        # Proses file upload jika ada
        uploaded = form.file.data
        if uploaded and getattr(uploaded, 'filename', ''):
            if not _allowed_file(uploaded.filename):
                flash('Tipe file tidak diizinkan.', 'danger')
                return render_template('mahasiswa/submit_tugas.html', form=form, tugas=tugas)
            file_path, file_original = _save_upload(uploaded)

        submission = Submission(
            tugas_id=tugas_id,
            mahasiswa_id=current_user.id,
            konten=sanitize_input(form.konten.data or '', 5000) or None,
            file_path=file_path,
            file_original=file_original,
            link_url=sanitize_input(form.link_url.data or '', 500) or None,
        )
        db.session.add(submission)
        db.session.commit()
        flash('Tugas berhasil dikumpulkan!', 'success')
        return redirect(url_for('mahasiswa.dashboard'))

    return render_template('mahasiswa/submit_tugas.html', form=form, tugas=tugas)
