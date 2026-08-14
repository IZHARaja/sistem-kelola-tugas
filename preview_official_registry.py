import argparse

from app import create_app
from app.official_registry import read_registry_rows


def parse_args():
    parser = argparse.ArgumentParser(description='Tampilkan preview data workbook resmi siswa atau guru.')
    parser.add_argument('--role', choices=['siswa', 'guru', 'all'], default='all', help='Jenis data yang ditampilkan.')
    parser.add_argument('--limit', type=int, default=10, help='Jumlah baris preview per role.')
    return parser.parse_args()


def preview_block(title, rows, limit):
    print(f'[{title}] total={len(rows)}')
    for row in rows[:limit]:
        print(row)
    print('')


def main():
    args = parse_args()
    app = create_app()

    siswa_rows = read_registry_rows(app.config['SISWA_REGISTRY_FILE'])
    guru_rows = read_registry_rows(app.config['GURU_REGISTRY_FILE'])

    if args.role in ('siswa', 'all'):
        preview_block('SISWA', siswa_rows, args.limit)
    if args.role in ('guru', 'all'):
        preview_block('GURU', guru_rows, args.limit)


if __name__ == '__main__':
    main()