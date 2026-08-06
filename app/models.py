from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='mahasiswa')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    tugas_dibuat = db.relationship('Tugas', backref='dosen', lazy='dynamic',
                                   foreign_keys='Tugas.dosen_id')
    submissions = db.relationship('Submission', backref='mahasiswa', lazy='dynamic',
                                  foreign_keys='Submission.mahasiswa_id')

    def set_password(self, password):
        # PBKDF2-SHA256 dengan 600.000 iterasi sesuai rekomendasi OWASP 2024
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:600000')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Tugas(db.Model):
    __tablename__ = 'tugas'

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    dosen_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submissions = db.relationship('Submission', backref='tugas', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tugas {self.judul}>'


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    tugas_id = db.Column(db.Integer, db.ForeignKey('tugas.id', ondelete='CASCADE'), nullable=False)
    mahasiswa_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    konten = db.Column(db.Text, nullable=True)       # Teks deskripsi (opsional)
    file_path = db.Column(db.String(300), nullable=True)  # Nama file tersimpan (opsional)
    file_original = db.Column(db.String(300), nullable=True)  # Nama asli file
    link_url = db.Column(db.String(500), nullable=True)  # URL/link (opsional)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        # Unique constraint mencegah duplikasi submission (mitigasi logic flaw)
        db.UniqueConstraint('tugas_id', 'mahasiswa_id', name='uq_submission_tugas_mahasiswa'),
    )

    def __repr__(self):
        return f'<Submission tugas={self.tugas_id} mhs={self.mahasiswa_id}>'


class SecurityLog(db.Model):
    """Tabel audit trail untuk event keamanan."""
    __tablename__ = 'security_logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(50), nullable=False)  # LOGIN_SUCCESS, LOGIN_FAIL, LOGOUT, dll
    username = db.Column(db.String(64), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(250), nullable=True)
    details = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SecurityLog {self.event_type} @ {self.timestamp}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
