from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL
from .models import User

ALLOWED_UPLOAD = ['pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg', 'ppt', 'pptx', 'xlsx', 'xls']


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        'Konfirmasi Password',
        validators=[DataRequired(), EqualTo('password', message='Password tidak cocok.')]
    )
    role = SelectField(
        'Daftar sebagai',
        choices=[('mahasiswa', 'Mahasiswa'), ('dosen', 'Dosen')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Buat Akun')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username sudah digunakan.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email sudah terdaftar.')


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
                     validators=[Optional(),
                                 FileAllowed(ALLOWED_UPLOAD, 'Format tidak didukung. Gunakan: PDF, DOC, DOCX, ZIP, gambar, dll.')])
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
