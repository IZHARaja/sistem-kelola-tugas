"""
Pytest fixtures shared across all tests.
"""
import os
import pytest
from app import create_app, db as _db
from app.official_registry import (
    GURU_HEADERS,
    SISWA_HEADERS,
    append_registry_row,
    write_registry_workbook,
)
from app.models import User, Tugas, Submission
from datetime import timedelta
from app.time_utils import utc_now


@pytest.fixture(scope='session')
def official_registry_files(tmp_path_factory):
    folder = tmp_path_factory.mktemp('official_registry')
    siswa_file = folder / 'siswa_resmi.xlsx'
    guru_file = folder / 'guru_resmi.xlsx'
    write_registry_workbook(str(siswa_file), SISWA_HEADERS, sheet_name='Data Siswa Resmi')
    write_registry_workbook(str(guru_file), GURU_HEADERS, sheet_name='Data Guru Resmi')
    return {
        'folder': str(folder),
        'siswa_file': str(siswa_file),
        'guru_file': str(guru_file),
    }


@pytest.fixture(scope='session')
def app(official_registry_files):
    """Create application with in-memory SQLite for tests."""
    test_app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'SERVER_NAME': 'localhost',
        'RATELIMIT_ENABLED': False,
        'OFFICIAL_DATA_FOLDER': official_registry_files['folder'],
        'SISWA_REGISTRY_FILE': official_registry_files['siswa_file'],
        'GURU_REGISTRY_FILE': official_registry_files['guru_file'],
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide clean DB for each test function."""
    with app.app_context():
        write_registry_workbook(app.config['SISWA_REGISTRY_FILE'], SISWA_HEADERS, sheet_name='Data Siswa Resmi')
        write_registry_workbook(app.config['GURU_REGISTRY_FILE'], GURU_HEADERS, sheet_name='Data Guru Resmi')
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def official_registry(app):
    class OfficialRegistryHelper:
        def add_siswa(self, *, nis, email, full_name, kelas='XII IPA 1', angkatan='2026'):
            append_registry_row(
                app.config['SISWA_REGISTRY_FILE'],
                SISWA_HEADERS,
                {
                    'NIS': nis,
                    'EMAIL': email,
                    'NAMA_LENGKAP': full_name,
                    'KELAS': kelas,
                    'ANGKATAN': angkatan,
                },
            )

        def add_guru(self, *, nip, email, full_name, mata_pelajaran='Informatika', status_pegawai='Tetap'):
            append_registry_row(
                app.config['GURU_REGISTRY_FILE'],
                GURU_HEADERS,
                {
                    'NIP': nip,
                    'EMAIL': email,
                    'NAMA_LENGKAP': full_name,
                    'MATA_PELAJARAN': mata_pelajaran,
                    'STATUS_PEGAWAI': status_pegawai,
                },
            )

    return OfficialRegistryHelper()


@pytest.fixture
def dosen_user(db):
    user = User(
        username='testdosen',
        full_name='Dosen Pengampu',
        nip='NIP001',
        email='dosen@test.com',
        role='dosen'
    )
    user.set_password('Dosen@1234!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def mahasiswa_user(db):
    user = User(
        username='testmhs',
        full_name='Mahasiswa Uji',
        nis='NIS001',
        email='mhs@test.com',
        role='mahasiswa'
    )
    user.set_password('Mhs@1234!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_tugas(db, dosen_user):
    tugas = Tugas(
        judul='Tugas Unit Test',
        deskripsi='Deskripsi tugas untuk unit testing.',
        deadline=utc_now() + timedelta(days=7),
        dosen_id=dosen_user.id,
    )
    db.session.add(tugas)
    db.session.commit()
    return tugas


def login(client, username, password):
    user = User.query.filter_by(username=username).first()
    identifier = user.nip if user.role == 'dosen' else user.nis
    return client.post('/login', data={
        'role': user.role,
        'identifier': identifier,
        'email': user.email,
        'full_name': user.full_name,
        'password': password,
    }, follow_redirects=True)
