# Software Requirements Specification (SRS)
## SiKelTugas — Sistem Kelola Tugas Mahasiswa
**Mata Kuliah:** Advanced Software Testing & Quality Assurance (ASTQA)  
**Versi:** 2.0 | **Tanggal:** 2026-08-07

---

## 1. Pendahuluan

### 1.1 Tujuan
Dokumen ini mendefinisikan kebutuhan fungsional dan non-fungsional untuk **SiKelTugas**, aplikasi web manajemen tugas mahasiswa berbasis Flask dengan desain antarmuka Neumorphism.

### 1.2 Ruang Lingkup
SiKelTugas memungkinkan Dosen mengelola tugas perkuliahan dan Mahasiswa mengumpulkan hasil pekerjaan secara digital, lengkap dengan fitur keamanan sesuai standar OWASP Top 10.

### 1.3 Definisi & Akronim
| Istilah | Keterangan |
|---|---|
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| RBAC | Role-Based Access Control |
| CSRF | Cross-Site Request Forgery |
| OWASP | Open Web Application Security Project |
| UAT | User Acceptance Testing |

---

## 2. Kebutuhan Fungsional (Functional Requirements)

### FR-01: Manajemen Akun & Autentikasi
| ID | Deskripsi | Prioritas |
|---|---|---|
| FR-01.1 | Sistem menyediakan halaman registrasi dengan field: username, email, password, role (Dosen/Mahasiswa) | Tinggi |
| FR-01.2 | Sistem memvalidasi kekuatan password (min. 8 karakter, kombinasi huruf besar/kecil, angka, simbol) | Tinggi |
| FR-01.3 | Sistem mengautentikasi pengguna melalui username dan password dengan hashing PBKDF2-SHA256 (600.000 iterasi) | Tinggi |
| FR-01.4 | Sistem menyediakan fungsi logout yang menghapus sesi aktif | Tinggi |
| FR-01.5 | Sistem membatasi percobaan login maks. 15 kali/menit per IP (rate limiting) | Tinggi |

### FR-02: Manajemen Tugas (Dosen)
| ID | Deskripsi | Prioritas |
|---|---|---|
| FR-02.1 | Dosen dapat membuat tugas baru dengan: judul, deskripsi, dan deadline | Tinggi |
| FR-02.2 | Dosen dapat mengedit tugas yang telah dibuat (hanya milik sendiri) | Tinggi |
| FR-02.3 | Dosen dapat menghapus tugas (cascade delete ke submission terkait) | Tinggi |
| FR-02.4 | Sistem menampilkan statistik tugas: total, aktif, dan jumlah submission | Sedang |

### FR-03: Pengumpulan Tugas (Mahasiswa)
| ID | Deskripsi | Prioritas |
|---|---|---|
| FR-03.1 | Mahasiswa dapat mengumpulkan tugas berupa teks deskripsi (maks. 5.000 karakter) | Tinggi |
| FR-03.2 | Mahasiswa dapat mengupload file dokumen (PDF, DOC, DOCX, TXT, ZIP, gambar, PPT, Excel — maks. 16 MB) | Tinggi |
| FR-03.3 | Mahasiswa dapat menyertakan URL/link (Google Drive, GitHub, OneDrive, dll.) | Tinggi |
| FR-03.4 | Sistem mencegah pengumpulan duplikat (satu mahasiswa satu submission per tugas) | Tinggi |
| FR-03.5 | Sistem memblokir pengumpulan setelah deadline terlewat | Tinggi |

### FR-04: Monitoring Submission (Dosen)
| ID | Deskripsi | Prioritas |
|---|---|---|
| FR-04.1 | Dosen dapat melihat semua submission untuk setiap tugas yang dibuatnya | Tinggi |
| FR-04.2 | Sistem menampilkan status ketepatan waktu (Tepat Waktu / Terlambat) | Sedang |
| FR-04.3 | Dosen dapat mengunduh file yang dikirim mahasiswa | Sedang |
| FR-04.4 | Dosen dapat membuka link URL yang disertakan mahasiswa | Sedang |

### FR-05: Keamanan & Audit Log
| ID | Deskripsi | Prioritas |
|---|---|---|
| FR-05.1 | Sistem mencatat setiap event keamanan: LOGIN_SUCCESS, LOGIN_FAIL, LOGOUT, REGISTER, ACCESS_DENIED | Tinggi |
| FR-05.2 | Setiap request diproteksi dengan token CSRF (expired 1 jam) | Tinggi |
| FR-05.3 | Sistem memvalidasi dan menyanitasi semua input pengguna (bleach strip) | Tinggi |
| FR-05.4 | Sistem menerapkan RBAC — endpoint Dosen tidak dapat diakses Mahasiswa, begitu pula sebaliknya | Tinggi |
| FR-05.5 | Sistem menerapkan IDOR protection — pengguna hanya dapat mengakses resource miliknya | Tinggi |

---

## 3. Kebutuhan Non-Fungsional (Non-Functional Requirements)

### NFR-01: Performance (Kinerja)
| ID | Deskripsi | Target |
|---|---|---|
| NFR-01.1 | Response time halaman dashboard | < 500 ms (95th percentile) |
| NFR-01.2 | Response time login/register | < 800 ms |
| NFR-01.3 | Upload file 10 MB | < 3 detik |
| NFR-01.4 | Throughput sistem | Min. 50 req/detik pada kondisi normal |

### NFR-02: Scalability (Skalabilitas)
| ID | Deskripsi | Target |
|---|---|---|
| NFR-02.1 | Sistem mampu menangani concurrent users | Min. 100 pengguna bersamaan |
| NFR-02.2 | Database mendukung pertumbuhan data | Min. 10.000 submission tanpa degradasi performa |
| NFR-02.3 | Arsitektur mendukung horizontal scaling melalui stateless session design | ✓ |

### NFR-03: Security (Keamanan)
| ID | Deskripsi | Standar |
|---|---|---|
| NFR-03.1 | Password hashing | PBKDF2-SHA256, 600.000 iterasi (OWASP 2024) |
| NFR-03.2 | Proteksi injeksi SQL | SQLAlchemy ORM parameterized query |
| NFR-03.3 | HTTP Security Headers | X-Content-Type-Options, X-Frame-Options, CSP, X-XSS-Protection |
| NFR-03.4 | Proteksi path traversal pada file upload | `werkzeug.utils.secure_filename` + UUID prefix |
| NFR-03.5 | Rate limiting | 15 req/menit login, 10 req/menit register per IP |

### NFR-04: Reliability & Availability
| ID | Deskripsi | Target |
|---|---|---|
| NFR-04.1 | Uptime sistem | 99% (non-production) |
| NFR-04.2 | Data integrity | Unique constraint pada submission (tugas_id + mahasiswa_id) |
| NFR-04.3 | Error handling | Halaman 403/404 custom yang informatif |

### NFR-05: Usability
| ID | Deskripsi | Target |
|---|---|---|
| NFR-05.1 | Antarmuka responsif (mobile-friendly) | Mendukung layar ≥ 320px |
| NFR-05.2 | Feedback visual untuk setiap aksi pengguna | Flash message success/error |
| NFR-05.3 | Password strength meter real-time | ✓ |

---

## 4. Batasan Sistem
- Platform: Web Browser (Chrome, Firefox, Edge versi terkini)
- Backend: Python 3.13, Flask 3.0
- Database: SQLite (development) / PostgreSQL (production)
- Hosting: Vercel (Serverless)
- Tidak mendukung akses offline
