import argparse

from app import create_app
from app.official_registry import GURU_HEADERS, SISWA_HEADERS, write_registry_workbook


KELAS_CYCLE = [
    'X RPL 1',
    'X RPL 2',
    'X TKJ 1',
    'XI RPL 1',
    'XI TKJ 1',
    'XII TKJ 1',
    'XII AKL 1',
    'XI MPLB 1',
]

GURU_CYCLE = [
    ('Matematika', 'Tetap'),
    ('Bahasa Indonesia', 'Tetap'),
    ('Informatika', 'Tetap'),
    ('Bahasa Inggris', 'Honorer'),
    ('Fisika', 'Tetap'),
    ('Kimia', 'Honorer'),
    ('Biologi', 'Tetap'),
    ('Sejarah', 'Honorer'),
    ('Ekonomi', 'Tetap'),
    ('PJOK', 'Honorer'),
]

NAME_PARTS = [
    'Adi', 'Aisyah', 'Akbar', 'Alya', 'Andi', 'Anisa', 'Bima', 'Cahya', 'Dewi', 'Dimas',
    'Fajar', 'Farah', 'Hafiz', 'Indah', 'Jihan', 'Kevin', 'Laras', 'Maya', 'Nabila', 'Nanda',
    'Putra', 'Putri', 'Rafi', 'Rani', 'Reza', 'Rizky', 'Salsa', 'Sinta', 'Tegar', 'Wahyu',
]

SURNAME_PARTS = [
    'Saputra', 'Pratama', 'Permata', 'Lestari', 'Wijaya', 'Kusuma', 'Ramadhan', 'Nugraha',
    'Hidayat', 'Maharani', 'Setiawan', 'Anggraini', 'Purnama', 'Sari', 'Utami', 'Firdaus',
]

TEACHER_PREFIXES = ['Ahmad', 'Dian', 'Eka', 'Fitri', 'Hendra', 'Intan', 'Lukman', 'Nina', 'Rahmat', 'Siti']


def build_person_name(index, first_parts, last_parts):
    first = first_parts[(index - 1) % len(first_parts)]
    middle = first_parts[((index * 3) - 1) % len(first_parts)]
    last = last_parts[((index * 5) - 1) % len(last_parts)]
    return f'{first} {middle} {last}'


def build_siswa_rows(count, domain):
    rows = []
    for index in range(1, count + 1):
        rows.append({
            'NIS': f'SISWA{index:04d}',
            'EMAIL': f'siswa{index:03d}@{domain}',
            'NAMA_LENGKAP': build_person_name(index, NAME_PARTS, SURNAME_PARTS),
            'KELAS': KELAS_CYCLE[(index - 1) % len(KELAS_CYCLE)],
            'ANGKATAN': str(2024 + ((index - 1) % 3)),
        })
    return rows


def build_guru_rows(count, domain):
    rows = []
    for index in range(1, count + 1):
        subject, status = GURU_CYCLE[(index - 1) % len(GURU_CYCLE)]
        rows.append({
            'NIP': f'GURU{index:04d}',
            'EMAIL': f'guru{index:03d}@{domain}',
            'NAMA_LENGKAP': build_person_name(index, TEACHER_PREFIXES, SURNAME_PARTS),
            'MATA_PELAJARAN': subject,
            'STATUS_PEGAWAI': status,
        })
    return rows


def parse_args():
    parser = argparse.ArgumentParser(description='Isi workbook resmi siswa dan guru dengan data sintetis.')
    parser.add_argument('--siswa', type=int, default=100, help='Jumlah data siswa sintetis.')
    parser.add_argument('--guru', type=int, default=123, help='Jumlah data guru sintetis.')
    parser.add_argument('--domain', default='smkncontoh.sch.id', help='Domain email yang dipakai.')
    return parser.parse_args()


def main():
    args = parse_args()
    app = create_app()

    siswa_rows = build_siswa_rows(args.siswa, args.domain)
    guru_rows = build_guru_rows(args.guru, args.domain)

    write_registry_workbook(
        app.config['SISWA_REGISTRY_FILE'],
        SISWA_HEADERS,
        siswa_rows,
        sheet_name='Data Siswa Resmi',
    )
    write_registry_workbook(
        app.config['GURU_REGISTRY_FILE'],
        GURU_HEADERS,
        guru_rows,
        sheet_name='Data Guru Resmi',
    )

    print({'siswa_written': len(siswa_rows), 'guru_written': len(guru_rows), 'domain': args.domain})


if __name__ == '__main__':
    main()