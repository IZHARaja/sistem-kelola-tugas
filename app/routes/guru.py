from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .. import db
from ..models import Tugas, Submission
from ..forms import TugasForm
from ..security import sanitize_input, log_security_event
from ..time_utils import utc_now

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')
dosen_bp = Blueprint('dosen', __name__, url_prefix='/dosen')


def guru_required(f):
    """Decorator: tolak akses jika bukan role guru (mitigasi Broken Access Control / IDOR)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'dosen':
            log_security_event(
                'ACCESS_DENIED',
                username=getattr(current_user, 'username', 'anonymous'),
                details=f'Akses tidak sah ke endpoint guru: {f.__name__}'
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated


dosen_required = guru_required


@guru_bp.route('/dashboard')
@dosen_bp.route('/dashboard')
@login_required
@guru_required
def dashboard():
    tugas_list = Tugas.query.filter_by(dosen_id=current_user.id)\
        .order_by(Tugas.created_at.desc()).all()
    now = utc_now()
    active_count = sum(1 for t in tugas_list if t.deadline > now)
    total_submissions = sum(t.submissions.count() for t in tugas_list)
    return render_template('guru/dashboard.html',
                           tugas_list=tugas_list,
                           active_count=active_count,
                           total_submissions=total_submissions)


@guru_bp.route('/tugas/buat', methods=['GET', 'POST'])
@dosen_bp.route('/tugas/buat', methods=['GET', 'POST'])
@login_required
@guru_required
def create_tugas():
    form = TugasForm()
    if form.validate_on_submit():
        tugas = Tugas(
            judul=sanitize_input(form.judul.data, 200),
            deskripsi=sanitize_input(form.deskripsi.data, 5000),
            deadline=form.deadline.data,
            dosen_id=current_user.id,  # Selalu gunakan ID dari sesi — mencegah IDOR
        )
        db.session.add(tugas)
        db.session.commit()
        flash('Tugas berhasil dibuat!', 'success')
        return redirect(url_for('guru.dashboard'))
    return render_template('guru/create_tugas.html', form=form,
                           title='Buat Tugas Baru', tugas=None)


@guru_bp.route('/tugas/<int:tugas_id>/edit', methods=['GET', 'POST'])
@dosen_bp.route('/tugas/<int:tugas_id>/edit', methods=['GET', 'POST'])
@login_required
@guru_required
def edit_tugas(tugas_id):
    # IDOR mitigation: filter dosen_id=current_user.id sebelum izinkan edit
    tugas = Tugas.query.filter_by(id=tugas_id, dosen_id=current_user.id).first_or_404()
    form = TugasForm(obj=tugas)
    if form.validate_on_submit():
        tugas.judul = sanitize_input(form.judul.data, 200)
        tugas.deskripsi = sanitize_input(form.deskripsi.data, 5000)
        tugas.deadline = form.deadline.data
        tugas.updated_at = utc_now()
        db.session.commit()
        flash('Tugas berhasil diperbarui!', 'success')
        return redirect(url_for('guru.dashboard'))
    return render_template('guru/create_tugas.html', form=form,
                           title='Edit Tugas', tugas=tugas)


@guru_bp.route('/tugas/<int:tugas_id>/hapus', methods=['POST'])
@dosen_bp.route('/tugas/<int:tugas_id>/hapus', methods=['POST'])
@login_required
@guru_required
def delete_tugas(tugas_id):
    # IDOR mitigation: verifikasi kepemilikan sebelum hapus
    tugas = Tugas.query.filter_by(id=tugas_id, dosen_id=current_user.id).first_or_404()
    judul = tugas.judul
    db.session.delete(tugas)
    db.session.commit()
    flash(f'Tugas "{judul}" berhasil dihapus.', 'success')
    return redirect(url_for('guru.dashboard'))


@guru_bp.route('/tugas/<int:tugas_id>/submissions')
@dosen_bp.route('/tugas/<int:tugas_id>/submissions')
@login_required
@guru_required
def view_submissions(tugas_id):
    # IDOR mitigation: verifikasi kepemilikan sebelum lihat submission
    tugas = Tugas.query.filter_by(id=tugas_id, dosen_id=current_user.id).first_or_404()
    submissions = Submission.query.filter_by(tugas_id=tugas_id)\
        .order_by(Submission.submitted_at.desc()).all()
    return render_template('guru/submissions.html', tugas=tugas, submissions=submissions)


@guru_bp.route('/tugas/<int:tugas_id>/submissions/<int:submission_id>')
@dosen_bp.route('/tugas/<int:tugas_id>/submissions/<int:submission_id>')
@login_required
@guru_required
def view_submission_detail(tugas_id, submission_id):
    tugas = Tugas.query.filter_by(id=tugas_id, dosen_id=current_user.id).first_or_404()
    submission = Submission.query.filter_by(id=submission_id, tugas_id=tugas.id).first_or_404()
    return render_template('guru/submission_detail.html', tugas=tugas, submission=submission)
