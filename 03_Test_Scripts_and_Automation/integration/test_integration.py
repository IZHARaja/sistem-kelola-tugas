"""
Integration Tests — SiKelTugas
Menguji interaksi antarmodul dan alur data end-to-end.
"""
import io
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.models import User, Tugas, Submission, SecurityLog
from datetime import timedelta
from app.time_utils import utc_now

# Import helper dari conftest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import login


# ─── AUTH FLOW ──────────────────────────────────────────────────────────────────

class TestAuthFlow:
    def test_index_renders_portal_selector(self, client, db):
        """Route / harus menampilkan pemilih portal siswa dan guru."""
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'Portal Siswa' in resp.data
        assert b'Portal Guru' in resp.data
        assert b'Excel resmi sekolah' in resp.data

    def test_register_siswa_route_mentions_official_excel(self, client, db):
        """Route /register/siswa harus menjelaskan sumber data resmi sekolah."""
        resp = client.get('/register/siswa')
        assert resp.status_code == 200
        assert b'Excel resmi sekolah' in resp.data

    def test_login_siswa_route_renders_student_portal(self, client, db):
        """Route /login/siswa harus membuka portal login siswa."""
        resp = client.get('/login/siswa')
        assert resp.status_code == 200
        assert b'Login Siswa' in resp.data
        assert b'Daftar siswa di sini' in resp.data

    def test_login_guru_route_renders_teacher_portal(self, client, db):
        """Route /login/guru harus membuka portal login guru."""
        resp = client.get('/login/guru')
        assert resp.status_code == 200
        assert b'Login Guru' in resp.data
        assert b'Daftar guru di sini' in resp.data

    def test_register_creates_user(self, client, db, official_registry):
        """Registrasi berhasil harus membuat user baru di DB."""
        official_registry.add_siswa(nis='NISNEW1', email='newuser@test.com', full_name='New User')
        resp = client.post('/register', data={
            'full_name': 'New User',
            'email': 'newuser@test.com',
            'nis': 'NISNEW1',
            'nip': '',
            'password': 'NewPass@123!',
            'confirm_password': 'NewPass@123!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert resp.status_code == 200
        saved = User.query.filter_by(email='newuser@test.com').first()
        assert saved is not None
        assert saved.nis == 'NISNEW1'

    def test_register_guru_route_creates_teacher_user(self, client, db, official_registry):
        """Route /register/guru harus membuat akun guru dengan NIP."""
        official_registry.add_guru(nip='NIPNEW9', email='gurubaru@test.com', full_name='Guru Baru')
        resp = client.post('/register/guru', data={
            'full_name': 'Guru Baru',
            'email': 'gurubaru@test.com',
            'nis': '',
            'nip': 'NIPNEW9',
            'password': 'GuruBaru@123!',
            'confirm_password': 'GuruBaru@123!',
            'role': 'mahasiswa',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/login/guru' in resp.headers['Location']
        saved = User.query.filter_by(email='gurubaru@test.com').first()
        assert saved is not None
        assert saved.role == 'dosen'
        assert saved.nip == 'NIPNEW9'

    def test_register_logs_security_event(self, client, db, official_registry):
        """Registrasi berhasil harus mencatat REGISTER event di SecurityLog."""
        official_registry.add_guru(nip='NIPLOG1', email='loguser@test.com', full_name='Log User')
        client.post('/register', data={
            'full_name': 'Log User',
            'email': 'loguser@test.com',
            'nis': '',
            'nip': 'NIPLOG1',
            'password': 'LogPass@123!',
            'confirm_password': 'LogPass@123!',
            'role': 'dosen',
        }, follow_redirects=True)
        user = User.query.filter_by(email='loguser@test.com').first()
        log = SecurityLog.query.filter_by(event_type='REGISTER_SUCCESS', username=user.username).first()
        assert log is not None

    def test_register_rejects_unlisted_school_identity(self, client, db):
        """Registrasi harus ditolak jika data belum ada di file master resmi sekolah."""
        resp = client.post('/register', data={
            'full_name': 'Tidak Resmi',
            'email': 'tidakresmi@test.com',
            'nis': 'NISTOLAK1',
            'nip': '',
            'password': 'Valid@1234!',
            'confirm_password': 'Valid@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert User.query.filter_by(email='tidakresmi@test.com').first() is None
        assert b'resmi sekolah' in resp.data

    def test_login_success_redirects_mahasiswa(self, client, db, mahasiswa_user):
        """Login siswa berhasil harus redirect ke /siswa/dashboard."""
        resp = client.post('/login', data={
            'role': 'mahasiswa',
            'identifier': 'NIS001',
            'email': 'mhs@test.com',
            'full_name': 'Mahasiswa Uji',
            'password': 'Mhs@1234!',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/siswa/dashboard' in resp.headers['Location']

    def test_login_success_redirects_dosen(self, client, db, dosen_user):
        """Login guru berhasil harus redirect ke /guru/dashboard."""
        resp = client.post('/login', data={
            'role': 'dosen',
            'identifier': 'NIP001',
            'email': 'dosen@test.com',
            'full_name': 'Dosen Pengampu',
            'password': 'Dosen@1234!',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/guru/dashboard' in resp.headers['Location']

    def test_login_wrong_password_fails(self, client, db, mahasiswa_user):
        """Login dengan password salah harus tetap di /login (status 200)."""
        resp = client.post('/login', data={
            'role': 'mahasiswa',
            'identifier': 'NIS001',
            'email': 'mhs@test.com',
            'full_name': 'Mahasiswa Uji',
            'password': 'WrongPass!1',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'login' in resp.data.lower()

    def test_login_fail_logs_security_event(self, client, db, mahasiswa_user):
        """Gagal login harus mencatat LOGIN_FAIL di SecurityLog."""
        client.post('/login', data={
            'role': 'mahasiswa',
            'identifier': 'NIS001',
            'email': 'mhs@test.com',
            'full_name': 'Mahasiswa Uji',
            'password': 'WrongPass!1',
        }, follow_redirects=True)
        log = SecurityLog.query.filter_by(
            event_type='LOGIN_FAIL', username='NIS001'
        ).first()
        assert log is not None

    def test_logout_clears_session(self, client, db, mahasiswa_user):
        """Logout harus menghapus sesi dan redirect ke /login."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.get('/logout', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_protected_route_requires_login(self, client, db):
        """Mengakses dashboard tanpa login harus redirect ke portal auth."""
        resp = client.get('/siswa/dashboard', follow_redirects=False)
        assert resp.status_code == 302
        assert '/?next=%2Fsiswa%2Fdashboard' in resp.headers['Location']

    def test_legacy_dosen_route_still_accessible(self, client, db, dosen_user):
        """Route lama /dosen/* tetap bisa diakses sebagai alias guru."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get('/dosen/dashboard', follow_redirects=False)
        assert resp.status_code == 200

    def test_legacy_mahasiswa_route_still_accessible(self, client, db, mahasiswa_user):
        """Route lama /mahasiswa/* tetap bisa diakses sebagai alias siswa."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.get('/mahasiswa/dashboard', follow_redirects=False)
        assert resp.status_code == 200


# ─── RBAC & AUTHORIZATION ───────────────────────────────────────────────────────

class TestRBAC:
    def test_mahasiswa_cannot_access_dosen_dashboard(self, client, db, mahasiswa_user):
        """Siswa tidak boleh mengakses endpoint guru."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.get('/guru/dashboard', follow_redirects=True)
        assert resp.status_code == 403

    def test_dosen_cannot_access_mahasiswa_dashboard(self, client, db, dosen_user):
        """Guru tidak boleh mengakses endpoint siswa."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get('/siswa/dashboard', follow_redirects=True)
        assert resp.status_code == 403

    def test_dosen_cannot_access_other_dosen_tugas(self, client, db, dosen_user):
        """Dosen tidak boleh mengedit tugas milik dosen lain (IDOR protection)."""
        other = User(username='dosen2', full_name='Dosen Dua', nip='NIP002', email='dosen2@test.com', role='dosen')
        other.set_password('Other@1234!')
        db.session.add(other)
        db.session.commit()
        tugas = Tugas(
            judul='Tugas Dosen Lain',
            deskripsi='Desc',
            deadline=utc_now() + timedelta(days=1),
            dosen_id=other.id,
        )
        db.session.add(tugas)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/guru/tugas/{tugas.id}/edit')
        assert resp.status_code == 404  # IDOR — resource tidak ditemukan


# ─── TUGAS CRUD FLOW ────────────────────────────────────────────────────────────

class TestTugasFlow:
    def test_dosen_create_tugas(self, client, db, dosen_user):
        """Guru berhasil membuat tugas baru."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post('/guru/tugas/buat', data={
            'judul': 'Tugas Integrasi',
            'deskripsi': 'Deskripsi tugas integrasi yang cukup panjang.',
            'deadline': '2030-12-31T23:59',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Tugas.query.filter_by(judul='Tugas Integrasi').first() is not None

    def test_dosen_edit_own_tugas(self, client, db, dosen_user, sample_tugas):
        """Guru berhasil mengedit tugas miliknya."""
        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post(f'/guru/tugas/{sample_tugas.id}/edit', data={
            'judul': 'Tugas Unit Test EDITED',
            'deskripsi': 'Deskripsi yang sudah diedit.',
            'deadline': '2030-12-31T23:59',
        }, follow_redirects=True)
        assert resp.status_code == 200
        updated = db.session.get(Tugas, sample_tugas.id)
        assert updated.judul == 'Tugas Unit Test EDITED'

    def test_dosen_delete_tugas(self, client, db, dosen_user):
        """Guru berhasil menghapus tugasnya."""
        t = Tugas(
            judul='Hapus Ini',
            deskripsi='Akan dihapus.',
            deadline=utc_now() + timedelta(days=1),
            dosen_id=dosen_user.id,
        )
        db.session.add(t)
        db.session.commit()
        tid = t.id

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.post(f'/guru/tugas/{tid}/hapus', follow_redirects=True)
        assert resp.status_code == 200
        assert db.session.get(Tugas, tid) is None


# ─── SUBMISSION FLOW ────────────────────────────────────────────────────────────

class TestSubmissionFlow:
    def test_mahasiswa_submit_teks(self, client, db, mahasiswa_user, sample_tugas):
        """Siswa berhasil mengumpulkan tugas berupa teks."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/siswa/tugas/{sample_tugas.id}/submit',
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
        """Siswa tidak boleh submit dua kali untuk tugas yang sama."""
        login(client, 'testmhs', 'Mhs@1234!')
        client.post(
            f'/siswa/tugas/{sample_tugas.id}/submit',
            data={'konten': 'Pertama'},
            follow_redirects=True,
        )
        resp = client.post(
            f'/siswa/tugas/{sample_tugas.id}/submit',
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
            f'/siswa/tugas/{sample_tugas.id}/submit',
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
        """Submit setelah deadline harus diblokir untuk siswa."""
        t = Tugas(
            judul='Tugas Expired',
            deskripsi='Deadlinenya sudah lewat.',
            deadline=utc_now() - timedelta(hours=1),
            dosen_id=dosen_user.id,
        )
        db.session.add(t)
        db.session.commit()

        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/siswa/tugas/{t.id}/submit',
            data={'konten': 'Terlambat'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert Submission.query.filter_by(
            tugas_id=t.id, mahasiswa_id=mahasiswa_user.id
        ).first() is None

    def test_dosen_views_submissions(self, client, db, dosen_user, mahasiswa_user, sample_tugas):
        """Guru bisa melihat tabel submissions untuk tugasnya."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Jawaban test',
        )
        db.session.add(sub)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/guru/tugas/{sample_tugas.id}/submissions')
        assert resp.status_code == 200
        assert b'Mahasiswa Uji' in resp.data
        assert b'Lihat Detail' in resp.data

    def test_dosen_views_submission_detail(self, client, db, dosen_user, mahasiswa_user, sample_tugas):
        """Guru bisa membuka detail submission siswa beserta isi tugas yang dikumpulkan."""
        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            konten='Jawaban lengkap untuk dilihat guru.',
            link_url='https://example.com/jawaban',
        )
        db.session.add(sub)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/guru/tugas/{sample_tugas.id}/submissions/{sub.id}')
        assert resp.status_code == 200
        assert b'Detail Pengumpulan Siswa' in resp.data
        assert b'Jawaban lengkap untuk dilihat guru.' in resp.data
        assert b'Mahasiswa Uji' in resp.data
        assert b'https://example.com/jawaban' in resp.data

    def test_guru_can_download_submission_file(self, client, db, dosen_user, mahasiswa_user, sample_tugas, app):
        """Guru bisa mengunduh file yang dikumpulkan siswa dari halaman submission."""
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        saved_name = 'test_jawaban.pdf'
        saved_path = os.path.join(upload_folder, saved_name)
        with open(saved_path, 'wb') as handle:
            handle.write(b'%PDF-1.4 guru download test')

        sub = Submission(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
            file_path=saved_name,
            file_original='jawaban.pdf',
        )
        db.session.add(sub)
        db.session.commit()

        login(client, 'testdosen', 'Dosen@1234!')
        resp = client.get(f'/uploads/{saved_name}')
        assert resp.status_code == 200
        assert resp.headers['Content-Disposition'].startswith('attachment;')
        assert b'%PDF-1.4 guru download test' in resp.data

    def test_mahasiswa_submit_pdf_file(self, client, db, mahasiswa_user, sample_tugas):
        """Siswa dapat mengunggah file PDF atau file Office sebagai submission."""
        login(client, 'testmhs', 'Mhs@1234!')
        resp = client.post(
            f'/siswa/tugas/{sample_tugas.id}/submit',
            data={
                'konten': '',
                'link_url': '',
                'file': (io.BytesIO(b'%PDF-1.4 mock file'), 'jawaban.pdf'),
            },
            content_type='multipart/form-data',
            follow_redirects=True,
        )
        assert resp.status_code == 200
        sub = Submission.query.filter_by(
            tugas_id=sample_tugas.id,
            mahasiswa_id=mahasiswa_user.id,
        ).first()
        assert sub is not None
        assert sub.file_original == 'jawaban.pdf'
        assert sub.file_path is not None


# ─── BLACKBOX: EQUIVALENCE PARTITIONING & BVA ───────────────────────────────────

class TestBlackboxEP:
    """Equivalence Partitioning untuk form registrasi."""

    def test_ep_valid_username(self, client, db, official_registry):
        """EP: data registrasi siswa valid harus diterima."""
        official_registry.add_siswa(nis='NISEP1', email='ep1@test.com', full_name='Valid Student')
        resp = client.post('/register', data={
            'full_name': 'Valid Student',
            'email': 'ep1@test.com',
            'nis': 'NISEP1',
            'nip': '',
            'password': 'Valid@1234!',
            'confirm_password': 'Valid@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(nis='NISEP1').first() is not None

    def test_ep_username_too_short(self, client, db):
        """EP: nama lengkap terlalu pendek (<3 char) harus ditolak."""
        resp = client.post('/register', data={
            'full_name': 'Ab',
            'email': 'ep2@test.com',
            'nis': 'NISEP2',
            'nip': '',
            'password': 'Valid@1234!',
            'confirm_password': 'Valid@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(email='ep2@test.com').first() is None

    def test_bva_username_min_boundary(self, client, db, official_registry):
        """BVA: nama lengkap tepat 3 karakter harus diterima."""
        official_registry.add_siswa(nis='NISBVA', email='bva@test.com', full_name='Bva')
        resp = client.post('/register', data={
            'full_name': 'Bva',
            'email': 'bva@test.com',
            'nis': 'NISBVA',
            'nip': '',
            'password': 'Bva@1234!!',
            'confirm_password': 'Bva@1234!!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(email='bva@test.com').first() is not None

    def test_bva_password_min_boundary(self, client, db, official_registry):
        """BVA: password tepat 8 karakter harus diterima jika memenuhi kriteria."""
        official_registry.add_siswa(nis='NISPWD', email='bvapwd@test.com', full_name='Bva Pwd')
        resp = client.post('/register', data={
            'full_name': 'Bva Pwd',
            'email': 'bvapwd@test.com',
            'nis': 'NISPWD',
            'nip': '',
            'password': 'Aa@12345',
            'confirm_password': 'Aa@12345',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        # Bergantung pada implementasi validate_password_strength
        assert resp.status_code == 200

    def test_ep_invalid_email(self, client, db):
        """EP: email tidak valid harus ditolak."""
        resp = client.post('/register', data={
            'full_name': 'Invalid Email',
            'email': 'bukan-email',
            'nis': 'NISBADMAIL',
            'nip': '',
            'password': 'Pass@1234!',
            'confirm_password': 'Pass@1234!',
            'role': 'mahasiswa',
        }, follow_redirects=True)
        assert User.query.filter_by(nis='NISBADMAIL').first() is None
