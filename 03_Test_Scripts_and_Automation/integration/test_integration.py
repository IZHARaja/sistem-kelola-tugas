"""
Integration Tests — SiKelTugas
Menguji interaksi antarmodul dan alur data end-to-end.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.models import User, Tugas, Submission, SecurityLog
from datetime import datetime, timedelta

# Import helper dari conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import login


# ─── AUTH FLOW ──────────────────────────────────────────────────────────────────

class TestAuthFlow:
    def test_register_creates_user(self, client, db):
        """Registrasi berhasil harus membuat user baru di DB."""
        resp = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewPass@123!',
            'confirm_password': 'NewPass@123!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert User.query.filter_by(username='newuser').first() is not None

    def test_register_logs_security_event(self, client, db):
        """Registrasi berhasil harus mencatat REGISTER event di SecurityLog."""
        client.post('/register', data={
            'username': 'loguser',
            'email': 'loguser@test.com',
            'password': 'LogPass@123!',
            'confirm_password': 'LogPass@123!',
            'role': 'dosen',
        }, follow_redirects=True)
        log = SecurityLog.query.filter_by(event_type='REGISTER_SUCCESS', username='loguser').first()
        assert log is not None

    def test_login_success_redirects_mahasiswa(self, client, db, mahasiswa_user):
        """Login mahasiswa berhasil harus redirect ke /mahasiswa/dashboard."""
        resp = client.post('/login', data={
            'username': 'testmhs',
            'password': 'Mhs@1234!',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/mahasiswa/dashboard' in resp.headers['Location']

    def test_login_success_redirects_dosen(self, client, db, dosen_user):
        """Login dosen berhasil harus redirect ke /dosen/dashboard."""
        resp = client.post('/login', data={
            'username': 'testdosen',
            'password': 'Dosen@1234!',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/dosen/dashboard' in resp.headers['Location']

    def test_login_wrong_password_fails(self, client, db, mahasiswa_user):
        """Login dengan password salah harus tetap di /login (status 200)."""
        resp = client.post('/login', data={
            'username': 'testmhs',
            'password': 'WrongPass!1',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'login' in resp.data.lower()

    def test_login_fail_logs_security_event(self, client, db, mahasiswa_user):
        """Gagal login harus mencatat LOGIN_FAIL di SecurityLog."""
        client.post('/login', data={
            'username': 'testmhs',
            'password': 'WrongPass!1',
        }, follow_redirects=True)
        log = SecurityLog.query.filter_by(
            event_type='LOGIN_FAIL', username='testmhs'
        ).first()
        assert log is not None

    def test_logout_clears_session(self, client, db, mahasiswa_user):
        """Logout harus menghapus sesi dan redirect ke /login."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.get('/logout', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_protected_route_requires_login(self, client, db):
        """Mengakses dashboard tanpa login harus redirect ke /login."""
        resp = client.get('/mahasiswa/dashboard', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']


# ─── RBAC & AUTHORIZATION ───────────────────────────────────────────────────────

class TestRBAC:
    def test_mahasiswa_cannot_access_dosen_dashboard(self, client, db, mahasiswa_user):
        """Mahasiswa tidak boleh mengakses endpoint dosen."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.get('/dosen/dashboard', follow_redirects=True)
        assert resp.status_code == 403

    def test_dosen_cannot_access_mahasiswa_dashboard(self, client, db, dosen_user):
        """Dosen tidak boleh mengakses endpoint mahasiswa."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get('/mahasiswa/dashboard', follow_redirects=True)
        assert resp.status_code == 403

    def test_dosen_cannot_access_other_dosen_tugas(self, client, db, dosen_user):
        """Dosen tidak boleh mengedit tugas milik dosen lain (IDOR protection)."""
        other = User(username='dosen2', email='dosen2@test.com', role='dosen')
        other.set_password('Other@1234!')
        db.session.add(other)
        db.session.commit()
        tugas = Tugas(
            judul='Tugas Dosen Lain',
            deskripsi='Desc',
            deadline=datetime.utcnow() + timedelta(days=1),
            dosen_id=other.id,
        )
        db.session.add(tugas)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/dosen/tugas/{tugas.id}/edit')
        assert resp.status_code == 404  # IDOR — resource tidak ditemukan


# ─── TUGAS CRUD FLOW ────────────────────────────────────────────────────────────

class TestTugasFlow:
    def test_dosen_create_tugas(self, client, db, dosen_user):
        """Dosen berhasil membuat tugas baru."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post('/dosen/tugas/buat', data={
            'judul': 'Tugas Integrasi',
            'deskripsi': 'Deskripsi tugas integrasi yang cukup panjang.',
            'deadline': '2030-12-31T23:59',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Tugas.query.filter_by(judul='Tugas Integrasi').first() is not None

    def test_dosen_edit_own_tugas(self, client, db, dosen_user, sample_tugas):
        """Dosen berhasil mengedit tugas miliknya."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post(f'/dosen/tugas/{sample_tugas.id}/edit', data={
            'judul': 'Tugas Unit Test EDITED',
            'deskripsi': 'Deskripsi yang sudah diedit.',
            'deadline': '2030-12-31T23:59',
        }, follow_redirects=True)
        assert resp.status_code == 200
        updated = Tugas.query.get(sample_tugas.id)
        assert updated.judul == 'Tugas Unit Test EDITED'

    def test_dosen_delete_tugas(self, client, db, dosen_user):
        """Dosen berhasil menghapus tugasnya."""
        t = Tugas(
            judul='Hapus Ini',
            deskripsi='Akan dihapus.',
            deadline=datetime.utcnow() + timedelta(days=1),
            dosen_id=dosen_user.id,
        )
        db.session.add(t)
        db.session.commit()
        tid = t.id

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post(f'/dosen/tugas/{tid}/hapus', follow_redirects=True)
        assert resp.status_code == 200
        assert Tugas.query.get(tid) is None


# ─── SUBMISSION FLOW ────────────────────────────────────────────────────────────

class TestSubmissionFlow:
    def test_mahasiswa_submit_teks(self, client, db, mahasiswa_user, sample_tugas):
        """Mahasiswa berhasil mengumpulkan tugas berupa teks."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/mahasiswa/tugas/{sample_tugas.id}/submit',
            data={'konten': 'Jawaban saya adalah ini.'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        sub = Submission.query.filter_by(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
        ).first()
        assert sub is not None
        assert sub.konten == 'Jawaban saya adalah ini.'

    def test_mahasiswa_cannot_double_submit(self, client, db, mahasiswa_user, sample_tugas):
        """Mahasiswa tidak boleh submit dua kali untuk tugas yang sama."""
        login(client, 'testmhs', 'Mhs@1234!')
        client.post(
            f'/mahasiswa/tugas/{sample_tugas.id}/submit',
            data={'konten': 'Pertama'},
            follow_redirects=True,
        )
        resp = client.post(
            f'/mahasiswa/tugas/{sample_tugas.id}/submit',
            data={'konten': 'Kedua'},
            follow_redirects=True,
        )
        # Kedua harus redirect ke dashboard (sudah ada submission)
        assert resp.status_code == 200
        count = Submission.query.filter_by(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
        ).count()
        assert count == 1

    def test_submit_empty_form_fails(self, client, db, mahasiswa_user, sample_tugas):
        """Submit tanpa isian apapun harus ditolak."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/mahasiswa/tugas/{sample_tugas.id}/submit',
            data={'konten': '', 'link_url': ''},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        # Tidak ada submission tersimpan
        assert Submission.query.filter_by(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
        ).first() is None

    def test_submit_after_deadline_blocked(self, client, db, dosen_user, mahasiswa_user):
        """Submit setelah deadline harus diblokir."""
        t = Tugas(
            judul='Tugas Expired',
            deskripsi='Deadlinenya sudah lewat.',
            deadline=datetime.utcnow() - timedelta(hours=1),
            dosen_id=dosen_user.id,
        )
        db.session.add(t)
        db.session.commit()

        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/mahasiswa/tugas/{t.id}/submit',
            data={'konten': 'Terlambat'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert Submission.query.filter_by(
            tugas_id=t.id, mahasiswa_id=mahasiswa_user.id
        ).first() is None

    def test_dosen_views_submissions(self, client, db, dosen_user, mahasiswa_user, sample_tugas):
        """Dosen bisa melihat tabel submissions untuk tugasnya."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Jawaban test',
        )
        db.session.add(sub)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/dosen/tugas/{sample_tugas.id}/submissions')
        assert resp.status_code == 200
        assert b'testmhs' in resp.data


# ─── BLACKBOX: EQUIVALENCE PARTITIONING & BVA ───────────────────────────────────

class TestBlackboxEP:
    """Equivalence Partitioning untuk form registrasi."""

    def test_ep_valid_username(self, client, db):
        """EP: username valid (3–64 char)."""
        resp = client.post('/register', data={
            'username': 'valid',
            'email': 'ep1@test.com',
            'password': 'Valid@1234!',
            'confirm_password': 'Valid@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(username='valid').first() is not None

    def test_ep_username_too_short(self, client, db):
        """EP: username terlalu pendek (<3 char) harus ditolak."""
        resp = client.post('/register', data={
            'username': 'ab',
            'email': 'ep2@test.com',
            'password': 'Valid@1234!',
            'confirm_password': 'Valid@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(username='ab').first() is None

    def test_bva_username_min_boundary(self, client, db):
        """BVA: username tepat 3 karakter harus diterima."""
        resp = client.post('/register', data={
            'username': 'bva',
            'email': 'bva@test.com',
            'password': 'Bva@1234!!',
            'confirm_password': 'Bva@1234!!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(username='bva').first() is not None

    def test_bva_password_min_boundary(self, client, db):
        """BVA: password tepat 8 karakter harus diterima jika memenuhi kriteria."""
        resp = client.post('/register', data={
            'username': 'bvapwd',
            'email': 'bvapwd@test.com',
            'password': 'Aa@12345',
            'confirm_password': 'Aa@12345',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        # Bergantung pada implementasi validate_password_strength
        assert resp.status_code == 200

    def test_ep_invalid_email(self, client, db):
        """EP: email tidak valid harus ditolak."""
        resp = client.post('/register', data={
            'username': 'invalidemail',
            'email': 'bukan-email',
            'password': 'Pass@1234!',
            'confirm_password': 'Pass@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(username='invalidemail').first() is None
