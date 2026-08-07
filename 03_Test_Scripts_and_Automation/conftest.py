"""
Pytest fixtures shared across all tests.
"""
import pytest
from app import create_app, db as _db
from app.models import User, Tugas, Submission
from datetime import datetime, timedelta


@pytest.fixture(scope='session')
def app():
    """Create application with in-memory SQLite for tests."""
    test_app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'SERVER_NAME': 'localhost',
        'RATELIMIT_ENABLED': False,
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide clean DB for each test function."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def dosen_user(db):
    user = User(username='testdosen', email='dosen@test.com', role='dosen')
    user.set_password('Dosen@1234!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def mahasiswa_user(db):
    user = User(username='testmhs', email='mhs@test.com', role='mahasiswa')
    user.set_password('Mhs@1234!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_tugas(db, dosen_user):
    tugas = Tugas(
        judul='Tugas Unit Test',
        deskripsi='Deskripsi tugas untuk unit testing.',
        deadline=datetime.utcnow() + timedelta(days=7),
        dosen_id=dosen_user.id,
    )
    db.session.add(tugas)
    db.session.commit()
    return tugas


def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)
