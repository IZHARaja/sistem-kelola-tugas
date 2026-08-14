from pathlib import Path

from app import create_app, db
from app.models import User
from app.official_registry import normalize_email, normalize_identifier, normalize_name, read_registry_rows


ACCOUNT_SPECS = [
    {
        'label': 'Siswa Uji 1',
        'role': 'mahasiswa',
        'index': 0,
        'password': 'SiswaTes@123!',
    },
    {
        'label': 'Siswa Uji 2',
        'role': 'mahasiswa',
        'index': 1,
        'password': 'SiswaTes@123!',
    },
    {
        'label': 'Guru Uji 1',
        'role': 'dosen',
        'index': 0,
        'password': 'GuruTes@123!',
    },
    {
        'label': 'Guru Uji 2',
        'role': 'dosen',
        'index': 1,
        'password': 'GuruTes@123!',
    },
]


def build_username(role, identifier):
    base = f'{role}-{identifier.lower()}'[:64]
    candidate = base
    suffix = 1
    while User.query.filter_by(username=candidate).first():
        tail = f'-{suffix}'
        candidate = f'{base[:64 - len(tail)]}{tail}'
        suffix += 1
    return candidate


def ensure_user(spec, row):
    role = spec['role']
    password = spec['password']
    email = normalize_email(row['EMAIL'])
    full_name = normalize_name(row['NAMA_LENGKAP'])
    identifier = normalize_identifier(row['NIS'] if role == 'mahasiswa' else row['NIP'])

    existing = User.query.filter_by(email=email, role=role).first()
    if existing:
        existing.full_name = full_name
        existing.nis = identifier if role == 'mahasiswa' else None
        existing.nip = identifier if role == 'dosen' else None
        existing.is_active = True
        existing.set_password(password)
        return existing, False

    user = User(
        username=build_username(role, identifier),
        full_name=full_name,
        email=email,
        role=role,
        nis=identifier if role == 'mahasiswa' else None,
        nip=identifier if role == 'dosen' else None,
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    return user, True


def write_summary_file(account_rows):
    lines = [
        '# Kredensial Akun Uji Lokal',
        '',
        'Akun-akun ini dibuat dari data resmi sintetis yang sudah ada di workbook resmi.',
        '',
        '| Label | Role | NIS/NIP | Email | Nama Lengkap | Password |',
        '|---|---|---|---|---|---|',
    ]
    for row in account_rows:
        lines.append(
            f"| {row['label']} | {row['role_label']} | {row['identifier']} | {row['email']} | {row['full_name']} | {row['password']} |"
        )

    output_path = Path('01_Documents/Kredensial_Akun_Uji.md')
    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return output_path


def main():
    app = create_app()

    with app.app_context():
        siswa_rows = read_registry_rows(app.config['SISWA_REGISTRY_FILE'])
        guru_rows = read_registry_rows(app.config['GURU_REGISTRY_FILE'])

        if len(siswa_rows) < 2 or len(guru_rows) < 2:
            raise SystemExit('Data resmi siswa/guru belum cukup untuk membuat akun uji.')

        summary_rows = []
        created = 0
        updated = 0

        for spec in ACCOUNT_SPECS:
            source_rows = siswa_rows if spec['role'] == 'mahasiswa' else guru_rows
            row = source_rows[spec['index']]
            user, is_created = ensure_user(spec, row)
            created += int(is_created)
            updated += int(not is_created)
            summary_rows.append({
                'label': spec['label'],
                'role_label': 'Siswa' if spec['role'] == 'mahasiswa' else 'Guru',
                'identifier': user.nis or user.nip or user.username,
                'email': user.email,
                'full_name': user.full_name,
                'password': spec['password'],
            })

        db.session.commit()
        output_path = write_summary_file(summary_rows)

    print({'created': created, 'updated': updated, 'summary_file': str(output_path)})


if __name__ == '__main__':
    main()