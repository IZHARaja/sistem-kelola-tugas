from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL
from .models import User

ROLE_CHOICES = [('mahasiswa', 'Siswa'), ('dosen', 'Guru')]
ALLOWED_UPLOAD = [
    'pdf', 'doc', 'docx', 'txt', 'zip',
    'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp',
    'ppt', 'pptx', 'xlsx', 'xls'
]
UPLOAD_ACCEPT = '.pdf,.doc,.docx,.txt,.zip,.png,.jpg,.jpeg,.gif,.webp,.bmp,.ppt,.pptx,.xlsx,.xls'


class LoginForm(FlaskForm):
    role = SelectField('Login sebagai', choices=ROLE_CHOICES, validators=[DataRequired()])
    identifier = StringField('NIS / NIP', validators=[DataRequired(), Length(min=3, max=32)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')


class RegisterForm(FlaskForm):
    full_name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    nis = StringField('NIS', validators=[Optional(), Length(min=3, max=32)])
    nip = StringField('NIP', validators=[Optional(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        'Konfirmasi Password',
        validators=[DataRequired(), EqualTo('password', message='Password tidak cocok.')]
    )
    role = SelectField(
        'Daftar sebagai',
        choices=ROLE_CHOICES,
        validators=[DataRequired()]
    )
    submit = SubmitField('Buat Akun')

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators)
        if not rv:
            return False

        if self.role.data == 'mahasiswa' and not (self.nis.data or '').strip():
            self.nis.errors.append('NIS wajib diisi untuk akun siswa.')
            return False

        if self.role.data == 'dosen' and not (self.nip.data or '').strip():
            self.nip.errors.append('NIP wajib diisi untuk akun guru.')
            return False

        return True

    def validate_email(self, email):
        if User.query.filter_by(email=(email.data or '').strip().lower()).first():
            raise ValidationError('Email sudah terdaftar.')

    def validate_nis(self, nis):
        value = (nis.data or '').strip().upper()
        if value and User.query.filter_by(nis=value).first():
            raise ValidationError('NIS sudah digunakan.')

    def validate_nip(self, nip):
        value = (nip.data or '').strip().upper()
        if value and User.query.filter_by(nip=value).first():
            raise ValidationError('NIP sudah digunakan.')


class TugasForm(FlaskForm):
    judul = StringField('Judul Tugas', validators=[DataRequired(), Length(min=3, max=200)])
    deskripsi = TextAreaField('Deskripsi & Instruksi',
                              validators=[DataRequired(), Length(min=10, max=5000)])
    deadline = DateTimeLocalField('Deadline', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Simpan Tugas')


class SubmissionForm(FlaskForm):
    konten = TextAreaField('Deskripsi / Jawaban Teks',
                           validators=[Optional(), Length(max=5000)])
    file = FileField('Upload Dokumen',
                     render_kw={'accept': UPLOAD_ACCEPT},
                     validators=[Optional(),
                                 FileAllowed(ALLOWED_UPLOAD, 'Format tidak didukung. Gunakan: PDF, file Microsoft Office, ZIP, atau gambar.')])
    link_url = StringField('Link / URL',
                           validators=[Optional(), URL(require_tld=False), Length(max=500)])
    submit = SubmitField('Kumpulkan Tugas')

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators)
        if not rv:
            return False
        has_file = self.file.data and getattr(self.file.data, 'filename', '')
        if not self.konten.data and not has_file and not self.link_url.data:
            self.konten.errors.append(
                'Isi minimal salah satu: teks jawaban, upload file, atau link URL.'
            )
            return False
        return True
