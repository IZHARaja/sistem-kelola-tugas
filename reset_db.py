from app import create_app, db


def reset_database():
    app = create_app()
    database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')

    if not database_uri.startswith('sqlite:'):
        raise SystemExit('Reset dibatasi untuk SQLite. DATABASE aktif bukan SQLite.')

    with app.app_context():
        db.drop_all()
        db.create_all()

    print('Database SQLite berhasil di-reset.')
    print(f'DATABASE_URI: {database_uri}')


if __name__ == '__main__':
    reset_database()