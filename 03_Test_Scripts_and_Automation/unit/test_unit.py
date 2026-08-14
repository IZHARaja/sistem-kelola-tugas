"""
Unit Tests — SiKelTugas
Menguji fungsi/method individual secara terisolasi.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.models import User, Tugas, Submission
from app.security import sanitize_input, validate_password_strength
from datetime import timedelta
from app.time_utils import utc_now


# ─── USER MODEL ────────────────────────────────────────────────────────────────

class TestUserModel:
    def test_password_hashing_produces_hash(self, db):
        """set_password harus menyimpan hash, bukan plaintext."""
        u = User(username='u1', full_name='User Satu', nis='NISU1', email='u1@test.com', role='mahasiswa')
        u.set_password('Rahasia@99')
        assert u.password_hash is not None
        assert u.password_hash != 'Rahasia@99'

    def test_password_hash_uses_pbkdf2(self, db):
        """Hash harus menggunakan algoritma pbkdf2:sha256."""
        u = User(username='u2', full_name='User Dua', nis='NISU2', email='u2@test.com', role='mahasiswa')
        u.set_password('Test@1234!')
        assert u.password_hash.startswith('pbkdf2:sha256')

    def test_check_password_correct(self, db):
        """check_password harus return True untuk password yang benar."""
        u = User(username='u3', full_name='User Tiga', nis='NISU3', email='u3@test.com', role='mahasiswa')
        u.set_password('Correct@99!')
        assert u.check_password('Correct@99!') is True

    def test_check_password_wrong(self, db):
        """check_password harus return False untuk password yang salah."""
        u = User(username='u4', full_name='User Empat', nis='NISU4', email='u4@test.com', role='mahasiswa')
        u.set_password('Correct@99!')
        assert u.check_password('WrongPass!1') is False

    def test_user_default_is_active(self, db):
        """User baru harus aktif secara default."""
        u = User(username='u5', full_name='User Lima', nis='NISU5', email='u5@test.com', role='mahasiswa')
        u.set_password('Pass@1234!')
        db.session.add(u)
        db.session.commit()
        assert u.is_active is True

    def test_user_repr(self, db):
        """__repr__ harus mengembalikan string yang bermakna."""
        u = User(username='repruser', full_name='Repr User', nip='NIPR1', email='repr@test.com', role='dosen')
        assert 'Repr User' in repr(u)

    def test_username_is_unique(self, db):
        """Username duplikat harus raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        u1 = User(username='dupuser', full_name='Dup User Satu', nis='NISDUP1', email='dup1@test.com', role='mahasiswa')
        u1.set_password('Pass@1234!')
        u2 = User(username='dupuser', full_name='Dup User Dua', nis='NISDUP2', email='dup2@test.com', role='mahasiswa')
        u2.set_password('Pass@1234!')
        db.session.add(u1)
        db.session.commit()
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_email_is_unique(self, db):
        """Email duplikat harus raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        u1 = User(username='emailtest1', full_name='Email Test Satu', nis='NISEMAIL1', email='same@test.com', role='mahasiswa')
        u1.set_password('Pass@1234!')
        u2 = User(username='emailtest2', full_name='Email Test Dua', nis='NISEMAIL2', email='same@test.com', role='mahasiswa')
        u2.set_password('Pass@1234!')
        db.session.add(u1)
        db.session.commit()
        db.session.add(u2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# ─── TUGAS MODEL ────────────────────────────────────────────────────────────────

class TestTugasModel:
    def test_create_tugas(self, db, dosen_user):
        """Tugas harus tersimpan dengan atribut yang benar."""
        deadline = utc_now() + timedelta(days=3)
        t = Tugas(
            judul='Tugas Pemrograman',
            deskripsi='Buat program sorting.',
            deadline=deadline,
            dosen_id=dosen_user.id,
        )
        db.session.add(t)
        db.session.commit()
        saved = db.session.get(Tugas, t.id)
        assert saved.judul == 'Tugas Pemrograman'
        assert saved.dosen_id == dosen_user.id

    def test_tugas_repr(self, db, sample_tugas):
        """__repr__ harus menyertakan judul tugas."""
        assert 'Tugas Unit Test' in repr(sample_tugas)

    def test_tugas_cascade_delete(self, db, dosen_user):
        """Menghapus tugas harus ikut menghapus submissions."""
        t = Tugas(
            judul='Cascade Test',
            deskripsi='Desc.',
            deadline=utc_now() + timedelta(days=1),
            dosen_id=dosen_user.id,
        )
        mhs = User(username='cascmhs', full_name='Cascade Mhs', nis='NISCASC', email='casc@test.com', role='mahasiswa')
        mhs.set_password('Pass@1234!')
        db.session.add_all([t, mhs])
        db.session.commit()

        sub = Submission(tugas_id=t.id, mahasiswa_id=mhs.id, konten='Jawaban')
        db.session.add(sub)
        db.session.commit()

        db.session.delete(t)
        db.session.commit()
        assert Submission.query.filter_by(tugas_id=t.id).count() == 0


# ─── SUBMISSION MODEL ───────────────────────────────────────────────────────────

class TestSubmissionModel:
    def test_create_submission_text(self, db, sample_tugas, mahasiswa_user):
        """Submission teks harus tersimpan dengan benar."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Ini jawaban teks saya.',
        )
        db.session.add(sub)
        db.session.commit()
        saved = db.session.get(Submission, sub.id)
        assert saved.konten == 'Ini jawaban teks saya.'
        assert saved.file_path is None
        assert saved.link_url is None

    def test_create_submission_with_file(self, db, sample_tugas, mahasiswa_user):
        """Submission dengan file harus menyimpan file_path dan file_original."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            file_path='abc123_tugas.pdf',
            file_original='tugas.pdf',
        )
        db.session.add(sub)
        db.session.commit()
        assert sub.file_path == 'abc123_tugas.pdf'
        assert sub.file_original == 'tugas.pdf'

    def test_create_submission_with_url(self, db, sample_tugas, mahasiswa_user):
        """Submission dengan URL harus tersimpan."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            link_url='https://github.com/user/repo',
        )
        db.session.add(sub)
        db.session.commit()
        assert sub.link_url == 'https://github.com/user/repo'

    def test_submission_unique_constraint(self, db, sample_tugas, mahasiswa_user):
        """Duplikasi submission (tugas+mahasiswa sama) harus raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        sub1 = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Pertama',
        )
        db.session.add(sub1)
        db.session.commit()

        sub2 = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Duplikat',
        )
        db.session.add(sub2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_submission_repr(self, db, sample_tugas, mahasiswa_user):
        sub = Submission(tugas_id=sample_tugas.id, mahasiswa_id=mahasiswa_user.id, konten='x')
        assert 'Submission' in repr(sub)


# ─── SECURITY FUNCTIONS ─────────────────────────────────────────────────────────

class TestSanitizeInput:
    def test_strips_script_tag(self):
        """Script tag harus dihapus oleh sanitize_input."""
        result = sanitize_input('<script>alert("xss")</script>Hello')
        assert '<script>' not in result
        assert 'Hello' in result

    def test_strips_html_tags(self):
        """Tag HTML apapun harus dihapus."""
        result = sanitize_input('<b>bold</b> <i>italic</i>')
        assert '<b>' not in result
        assert '<i>' not in result
        assert 'bold' in result

    def test_strips_event_handlers(self):
        """Atribut event handler harus dihapus."""
        result = sanitize_input('<p onclick="evil()">text</p>')
        assert 'onclick' not in result

    def test_empty_string_returns_empty(self):
        result = sanitize_input('')
        assert result == ''

    def test_normal_text_unchanged(self):
        """Teks biasa tanpa HTML tidak boleh diubah."""
        text = 'Ini teks biasa 123'
        assert sanitize_input(text) == text

    def test_truncates_to_max_length(self):
        """Input melebihi max_length harus dipotong."""
        long_text = 'a' * 200
        result = sanitize_input(long_text, max_length=100)
        assert len(result) <= 100

    def test_sql_injection_attempt_sanitized(self):
        """String SQL injection tidak boleh dieksekusi sebagai query."""
        payload = "'; DROP TABLE users; --"
        result = sanitize_input(payload)
        # Tidak ada HTML tags, teks asli dipertahankan (SQLAlchemy menangani injeksi)
        assert result == payload


class TestValidatePasswordStrength:
    def test_strong_password_passes(self):
        ok, _ = validate_password_strength('Kuat@1234!')
        assert ok is True

    def test_too_short_fails(self):
        ok, msg = validate_password_strength('Ab@1')
        assert ok is False
        assert msg != ''

    def test_no_uppercase_fails(self):
        ok, _ = validate_password_strength('lemah@1234')
        assert ok is False

    def test_no_lowercase_fails(self):
        ok, _ = validate_password_strength('LEMAH@1234')
        assert ok is False

    def test_no_digit_fails(self):
        ok, _ = validate_password_strength('TanpaAngka!')
        assert ok is False

    def test_no_special_char_fails(self):
        ok, _ = validate_password_strength('TanpaSimbol1')
        assert ok is False
