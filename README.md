# SiKelTugas — Sistem Kelola Tugas Sekolah

> **Tugas UAS — Advanced Software Testing & Quality Assurance (ASTQA)**  
> Aplikasi web manajemen tugas sekolah berbasis Flask dengan desain Neumorphism dan implementasi keamanan OWASP Top 10.

[![Tests](https://img.shields.io/badge/Tests-62%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/Coverage-92%25-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue)]()
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)]()

---

## Demo
🔗 **Live:** https://sistem-kelola-tugas.vercel.app

---

## Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 🔐 Multi-Role Auth | Portal login/register terpisah untuk Guru dan Siswa berbasis data resmi sekolah |
| 📋 Manajemen Tugas | Guru dapat CRUD tugas dengan deadline |
| 📤 Submit 3-in-1 | Siswa submit via teks, upload file Office/PDF/gambar (16 MB), atau link URL |
| 🛡️ Keamanan OWASP | CSRF, Rate Limiting, IDOR, XSS Prevention, SQL Injection mitigation |
| 🗂️ Master Data Resmi | Workbook Excel siswa dan guru terpisah untuk identitas resmi sekolah |
| 📊 Audit Log | Semua event keamanan tercatat di database |
| 🎨 Neumorphism UI | Desain antarmuka Soft UI yang modern |

---

## Struktur Repository

```
sistem-kelola-tugas/
│
├── 01_Documents/                   # Dokumentasi proyek
│   ├── SRS.md                      # Software Requirements Specification
│   └── SDD.md                      # Software Design Document + ERD + API Contract
│
├── 02_Test_Plans_and_Reports/      # Laporan pengujian
│   ├── Test_Execution_Report.md    # Hasil eksekusi semua tests
│   ├── UAT_SignOff_Sheet.md        # User Acceptance Testing sign-off
│   └── coverage_html/              # Laporan HTML code coverage (92%)
│
├── 03_Test_Scripts_and_Automation/ # Script pengujian
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/
│   │   └── test_unit.py            # Unit tests (29 test cases)
│   ├── integration/
│   │   └── test_integration.py     # Integration tests (33 test cases)
│   ├── postman/
│   │   └── SiKelTugas_API_Collection.json  # Postman collection
│   └── jmeter/
│       └── SiKelTugas_LoadTest.jmx         # JMeter load test plan
│
├── app/                            # Source code aplikasi
│   ├── __init__.py                 # App factory
│   ├── config.py                   # Konfigurasi
│   ├── models.py                   # SQLAlchemy models
│   ├── forms.py                    # WTForms
│   ├── security.py                 # Sanitisasi & audit log
│   ├── routes/
│   │   ├── auth.py                 # Portal login, register, logout
│   │   ├── guru.py                 # Endpoint Guru (+ alias dosen)
│   │   └── siswa.py                # Endpoint Siswa (+ alias mahasiswa)
│   ├── templates/                  # Jinja2 HTML templates
│   └── static/                     # CSS & JavaScript
│
├── api/
│   └── index.py                    # Vercel entry point
├── vercel.json                     # Konfigurasi deploy Vercel
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Konfigurasi pytest
├── populate_official_registry.py   # Isi workbook resmi dengan data sintetis
├── preview_official_registry.py    # Preview data workbook resmi dari terminal
├── create_registered_test_accounts.py # Buat akun uji lokal dari data resmi sintetis
├── reset_db.py                     # Reset schema SQLite lokal
├── start.ps1                       # Helper start Windows yang membersihkan proses lama
└── run.py                          # Entry point lokal
```

---

## Teknologi

| Komponen | Teknologi |
|---|---|
| Backend | Python 3.13, Flask 3.0 |
| ORM | SQLAlchemy 2.0, Flask-SQLAlchemy 3.1 |
| Auth | Flask-Login 0.6 |
| Security | Flask-WTF (CSRF), Flask-Limiter, bleach, Werkzeug |
| Database | SQLite (dev), PostgreSQL (prod) |
| Testing | pytest 9.1.1, pytest-cov |
| API Testing | Postman |
| Load Testing | Apache JMeter 5.6 |
| Deploy | Vercel (Serverless) |
| UI | Neumorphism CSS, Font Awesome 6 |

---

## Hasil Pengujian

| Jenis Test | Tools | Test Cases | Status | Coverage |
|---|---|---|---|---|
| Unit Testing | pytest | 29 | ✅ 29/29 Pass | 92% |
| Integration Testing | pytest | 33 | ✅ 33/33 Pass | 92% |
| System / API Testing | Postman | 20+ requests | Lihat collection | - |
| Load Testing | JMeter | 50 users concurrent | Lihat .jmx | - |
| UAT | Manual + Sign-off | 20 skenario | Lihat sign-off sheet | - |

---

## Cara Menjalankan Lokal

### Prasyarat
- Python 3.13+

### Setup
```bash
# Clone repository
git clone https://github.com/IZHARaja/sistem-kelola-tugas.git
cd sistem-kelola-tugas

# Install dependencies
pip install -r requirements.txt

# Buat file .env
echo "SECRET_KEY=your-secret-key-here" > .env

# Buat database SQLite baru yang kosong
python reset_db.py

# Jalankan aplikasi
python run.py
```

Buka browser: `http://127.0.0.1:5000`

### Database Lokal SQLite
- Default database lokal aktif: `instance/sikeltugas.db`
- Database lama tetap bisa tersimpan sebagai backup: `instance/tugasapp.db`
- Data akun aplikasi hanya dibuat lewat form register. Tidak ada akun demo bawaan.
- Registrasi baru hanya diterima jika identitas ada pada file Excel resmi sekolah.
- File Excel resmi otomatis dibuat saat aplikasi pertama kali dijalankan:
	- `instance/official_data/siswa_resmi.xlsx`
	- `instance/official_data/guru_resmi.xlsx`
- Kedua file Excel dipakai sebagai template resmi dan sebaiknya diisi hanya dengan data sekolah asli.
- Untuk pengujian lokal cepat, workbook resmi saat ini sudah diisi data sintetis: 100 siswa dan 123 guru.
- Untuk membuat database kosong dari nol:

```bash
python reset_db.py
```

- Untuk mengisi ulang workbook resmi dengan data sintetis:

```bash
python populate_official_registry.py --siswa 100 --guru 123
```

- Untuk melihat preview data resmi yang tersedia dari terminal:

```bash
python preview_official_registry.py --role all --limit 10
```

- Untuk membuat akun uji lokal yang langsung bisa login dari data resmi sintetis:

```bash
python create_registered_test_accounts.py
```

- Kredensial akun uji yang dibuat akan ditulis ke file:

```text
01_Documents/Kredensial_Akun_Uji.md
```

### Format Excel Resmi Siswa
- Kolom wajib yang dipakai saat register: `NIS`, `EMAIL`, `NAMA_LENGKAP`
- Kolom tambahan yang sudah disiapkan: `KELAS`, `ANGKATAN`

### Format Excel Resmi Guru
- Kolom wajib yang dipakai saat register: `NIP`, `EMAIL`, `NAMA_LENGKAP`
- Kolom tambahan yang sudah disiapkan: `MATA_PELAJARAN`, `STATUS_PEGAWAI`

### Alur Pengisian Data Resmi
1. Jalankan aplikasi sekali agar workbook otomatis dibuat.
2. Buka file Excel siswa dan guru di folder `instance/official_data`.
3. Isi data resmi sekolah sesuai kolom yang tersedia.
4. Simpan file Excel.
5. Pengguna yang datanya cocok dengan file resmi baru bisa register dan kemudian login.

### Menjalankan di Windows PowerShell
```powershell
& "C:\Python313\python.exe" .\reset_db.py
& "C:\Python313\python.exe" .\populate_official_registry.py --siswa 100 --guru 123
& "C:\Python313\python.exe" .\create_registered_test_accounts.py
.\start.ps1
```

### Menjalankan Tests
```bash
# Semua tests dengan coverage
pytest 03_Test_Scripts_and_Automation --cov=app --cov-report=html:02_Test_Plans_and_Reports/coverage_html -v

# Buka laporan HTML coverage
start 02_Test_Plans_and_Reports/coverage_html/index.html
```

### Postman
1. Buka Postman
2. Import `03_Test_Scripts_and_Automation/postman/SiKelTugas_API_Collection.json`
3. Set variable `base_url = http://127.0.0.1:5000`
4. Jalankan Collection Runner

### JMeter
1. Buka Apache JMeter
2. File → Open → `03_Test_Scripts_and_Automation/jmeter/SiKelTugas_LoadTest.jmx`
3. Pastikan server Flask berjalan di port 5000
4. Klik Run (▶)

---

## Keamanan (OWASP Top 10 Mitigation)

| OWASP ID | Kategori | Implementasi |
|---|---|---|
| A01 | Broken Access Control | RBAC decorator, IDOR protection (filter_by owner) |
| A02 | Cryptographic Failures | PBKDF2-SHA256 600K iterasi, HTTPS di production |
| A03 | Injection | SQLAlchemy ORM parameterized queries |
| A04 | Insecure Design | Session timeout 30 menit, unique submission constraint |
| A05 | Security Misconfiguration | HTTP Security Headers (CSP, X-Frame-Options, X-XSS-Protection) |
| A07 | Auth Failures | Rate limiting, audit log, strong password validation |
| A08 | Software Integrity | CSRF token pada semua form POST |
| A09 | Logging Failures | SecurityLog table mencatat semua event penting |

---

## Tim Pengembang

| Nama | Role | NIM |
|---|---|---|
| ____IZHAR____________ | Backend + Testing | _105841109023_______________ |
| ______DEVI NIRWANA __________ | Frontend + UI/UX | ____105841121023 ____________ |
| _MUH.RIZKI AQIL AZ-ZIKRA ALIMUDDIN _______________ | Documentation + QA | _______105841109623 _________ |
| ____M ERWIN KHUSNAEDY ____________ | DevOps + Security | ___105841120623 _____________ |
