# SiKelTugas — Sistem Kelola Tugas Mahasiswa

> **Tugas UAS — Advanced Software Testing & Quality Assurance (ASTQA)**  
> Aplikasi web manajemen tugas mahasiswa berbasis Flask dengan desain Neumorphism dan implementasi keamanan OWASP Top 10.

[![Tests](https://img.shields.io/badge/Tests-53%20passed-brightgreen)]()
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
| 🔐 Multi-Role Auth | Login/Register sebagai Dosen atau Mahasiswa |
| 📋 Manajemen Tugas | Dosen dapat CRUD tugas dengan deadline |
| 📤 Submit 3-in-1 | Mahasiswa submit via Teks, Upload File (16 MB), atau Link URL |
| 🛡️ Keamanan OWASP | CSRF, Rate Limiting, IDOR, XSS Prevention, SQL Injection mitigation |
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
│   │   └── test_integration.py     # Integration tests (24 test cases)
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
│   │   ├── auth.py                 # Login, Register, Logout
│   │   ├── dosen.py                # Endpoint Dosen
│   │   └── mahasiswa.py            # Endpoint Mahasiswa
│   ├── templates/                  # Jinja2 HTML templates
│   └── static/                     # CSS & JavaScript
│
├── api/
│   └── index.py                    # Vercel entry point
├── vercel.json                     # Konfigurasi deploy Vercel
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Konfigurasi pytest
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
| Integration Testing | pytest | 24 | ✅ 24/24 Pass | 92% |
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

# Jalankan aplikasi
python run.py
```

Buka browser: `http://127.0.0.1:5000`

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
| ________________ | Backend + Testing | ________________ |
| ________________ | Frontend + UI/UX | ________________ |
| ________________ | Documentation + QA | ________________ |
| ________________ | DevOps + Security | ________________ |
