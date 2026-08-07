# Software Design Document (SDD)
## SiKelTugas — Sistem Kelola Tugas Mahasiswa
**Versi:** 2.0 | **Tanggal:** 2026-08-07

---

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                           │
│              Browser (Chrome / Firefox / Edge)                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────────┐
│                       CDN / LOAD BALANCER                       │
│                  Vercel Edge Network (Global)                   │
│          Static Assets Cached (CSS, JS, Images)                 │
└──────────┬──────────────────────────────────┬───────────────────┘
           │ Dynamic Requests                 │ Static Assets
┌──────────▼──────────────┐        ┌──────────▼───────────────────┐
│   SERVERLESS FUNCTION   │        │        VERCEL CDN            │
│     @vercel/python      │        │   /static/* cached globally  │
│   api/index.py → app    │        └──────────────────────────────┘
│                         │
│  ┌───────────────────┐  │
│  │   Flask App       │  │
│  │  ┌─────────────┐  │  │
│  │  │ Auth BP     │  │  │
│  │  │ Dosen BP    │  │  │
│  │  │ Mahasiswa BP│  │  │
│  │  └─────────────┘  │  │
│  │  ┌─────────────┐  │  │
│  │  │  Security   │  │  │
│  │  │  Middleware │  │  │
│  │  │ (CSRF, Rate │  │  │
│  │  │  Limit, CSP)│  │  │
│  │  └─────────────┘  │  │
│  └───────────────────┘  │
└──────────┬──────────────┘
           │ SQLAlchemy ORM
┌──────────▼──────────────┐        ┌──────────────────────────────┐
│       DATA LAYER        │        │       FILE STORAGE           │
│                         │        │                              │
│  SQLite (Development)   │        │  Local: instance/uploads/    │
│  PostgreSQL (Production)│        │  Vercel: /tmp/uploads/       │
│                         │        │  Future: AWS S3 / Cloudinary │
│  Tables:                │        └──────────────────────────────┘
│  - users                │
│  - tugas                │
│  - submissions          │
│  - security_logs        │
└─────────────────────────┘
```

### Komponen Utama

| Komponen | Teknologi | Fungsi |
|---|---|---|
| Load Balancer | Vercel Edge Network | Distribusi traffic, SSL termination |
| CDN | Vercel Global CDN | Cache static assets (CSS/JS) |
| Application Server | Flask 3.0 (Serverless) | Business logic, routing |
| ORM | SQLAlchemy 2.0 | Database abstraction, parameterized queries |
| Auth | Flask-Login 0.6 | Session management, `@login_required` |
| CSRF | Flask-WTF 1.2 | Token-based CSRF protection |
| Rate Limiter | Flask-Limiter 3.7 | DDoS & brute-force mitigation |
| Input Sanitizer | bleach 6.1 | XSS prevention |
| Password | Werkzeug PBKDF2 | Secure password hashing |

---

## 2. Entity Relationship Diagram (ERD)

```
┌──────────────────────┐         ┌──────────────────────┐
│        USERS         │         │        TUGAS         │
├──────────────────────┤         ├──────────────────────┤
│ PK  id          INT  │◄────┐   │ PK  id          INT  │
│     username    STR  │     │   │     judul       STR  │
│     email       STR  │     │   │     deskripsi   TEXT │
│     password_hash STR│     │   │     deadline    DTTM │
│     role        STR  │     └───│FK   dosen_id    INT  │
│     created_at  DTTM │         │     created_at  DTTM │
│     is_active   BOOL │         │     updated_at  DTTM │
└──────────────────────┘         └──────────┬───────────┘
           │                                │
           │                                │ 1:N
           │                     ┌──────────▼───────────┐
           │                     │      SUBMISSIONS     │
           │                     ├──────────────────────┤
           │                     │ PK  id          INT  │
           └────────────────────►│FK   mahasiswa_id INT  │
                                 │FK   tugas_id    INT  │
                                 │     konten      TEXT │
                                 │     file_path   STR  │
                                 │     file_original STR│
                                 │     link_url    STR  │
                                 │     submitted_at DTTM│
                                 │ UQ (tugas_id,        │
                                 │     mahasiswa_id)    │
                                 └──────────────────────┘

┌──────────────────────┐
│    SECURITY_LOGS     │
├──────────────────────┤
│ PK  id          INT  │
│     timestamp   DTTM │
│     event_type  STR  │
│     username    STR  │
│     ip_address  STR  │
│     user_agent  STR  │
│     details     TEXT │
└──────────────────────┘
```

### Relasi
| Relasi | Tipe | Constraint |
|---|---|---|
| User → Tugas | 1:N | `dosen_id` FK, CASCADE DELETE |
| User → Submission | 1:N | `mahasiswa_id` FK, CASCADE DELETE |
| Tugas → Submission | 1:N | `tugas_id` FK, CASCADE DELETE |
| (tugas_id, mahasiswa_id) | UNIQUE | Cegah duplikasi submission |

---

## 3. API Contract

### Base URL
- Development: `http://127.0.0.1:5000`
- Production: `https://sistem-kelola-tugas.vercel.app`

### Authentication Endpoints

#### POST /register
**Deskripsi:** Registrasi akun baru  
**Rate Limit:** 10 req/menit per IP  
**Request Body (form-data):**
```
username     : string (3-64 char, required)
email        : string (valid email, required)
password     : string (min 8 char, required)
confirm_pass : string (must match password)
role         : enum ['mahasiswa', 'dosen']
csrf_token   : string (required)
```
**Response:**
- `302 Redirect /login` — Sukses
- `200 OK` + form errors — Validasi gagal

#### POST /login
**Deskripsi:** Login pengguna  
**Rate Limit:** 15 req/menit per IP  
**Request Body (form-data):**
```
username   : string (required)
password   : string (required)
csrf_token : string (required)
```
**Response:**
- `302 Redirect /dosen/dashboard` atau `/mahasiswa/dashboard` — Sukses
- `200 OK` + form errors — Kredensial salah

#### GET /logout
**Deskripsi:** Logout & hapus sesi  
**Auth:** Login required  
**Response:** `302 Redirect /login`

---

### Dosen Endpoints (Prefix: /dosen)

#### GET /dosen/dashboard
**Auth:** Login required + role=dosen  
**Response:** `200 OK` HTML — daftar tugas milik dosen

#### GET /dosen/tugas/buat
**Auth:** Login required + role=dosen  
**Response:** `200 OK` HTML — form buat tugas

#### POST /dosen/tugas/buat
**Auth:** Login required + role=dosen  
**Request Body:**
```
judul      : string (3-200 char, required)
deskripsi  : string (10-5000 char, required)
deadline   : datetime-local (required)
csrf_token : string
```
**Response:**
- `302 Redirect /dosen/dashboard` — Sukses
- `200 OK` + form errors — Validasi gagal

#### GET /dosen/tugas/{id}/edit
**Auth:** Login required + role=dosen + owner=current_user  
**IDOR Protection:** `filter_by(id=id, dosen_id=current_user.id)`  
**Response:** `200 OK` HTML — form edit pre-filled

#### POST /dosen/tugas/{id}/edit
**Auth:** Login required + role=dosen + owner  
**Request Body:** Same as POST /dosen/tugas/buat  
**Response:** `302 Redirect /dosen/dashboard` — Sukses

#### POST /dosen/tugas/{id}/hapus
**Auth:** Login required + role=dosen + owner  
**Request Body:** `csrf_token`  
**Response:** `302 Redirect /dosen/dashboard`

#### GET /dosen/tugas/{id}/submissions
**Auth:** Login required + role=dosen + owner  
**Response:** `200 OK` HTML — tabel submissions

---

### Mahasiswa Endpoints (Prefix: /mahasiswa)

#### GET /mahasiswa/dashboard
**Auth:** Login required + role=mahasiswa  
**Response:** `200 OK` HTML — daftar tugas dengan status

#### GET /mahasiswa/tugas/{id}/submit
**Auth:** Login required + role=mahasiswa  
**Response:** `200 OK` HTML — form submission

#### POST /mahasiswa/tugas/{id}/submit
**Auth:** Login required + role=mahasiswa  
**Content-Type:** `multipart/form-data`  
**Request Body:**
```
konten     : string (0-5000 char, optional)
file       : file (optional, maks 16MB)
link_url   : string (valid URL, optional)
csrf_token : string
```
**Validation:** Minimal satu dari konten/file/link_url harus diisi  
**Response:**
- `302 Redirect /mahasiswa/dashboard` — Sukses
- `200 OK` + form errors — Validasi gagal
- `302 Redirect /mahasiswa/dashboard` + flash error — Deadline lewat / duplikasi

---

### File Endpoints

#### GET /uploads/{filename}
**Auth:** Login required  
**Security:** `os.path.basename()` — cegah path traversal  
**Response:** File download (as_attachment=True)

---

## 4. Security Architecture

### Defense-in-Depth Layers
```
Layer 1 (Network):    Vercel Edge — HTTPS, DDoS mitigation
Layer 2 (App):        Rate Limiting — Flask-Limiter
Layer 3 (Session):    CSRF Token — Flask-WTF
Layer 4 (Auth):       Flask-Login, PBKDF2-SHA256
Layer 5 (AuthZ):      RBAC decorator (@dosen_required, @mahasiswa_required)
Layer 6 (Data):       IDOR protection, SQLAlchemy parameterized queries
Layer 7 (Input):      bleach sanitization, WTForms validation
Layer 8 (Headers):    CSP, X-Frame-Options, X-Content-Type-Options
Layer 9 (Audit):      SecurityLog table (semua event tercatat)
```

---

## 5. Deployment Architecture

```
Developer → git push → GitHub → Vercel CI/CD → Vercel Serverless
                                     ↓
                              Auto-deploy on push to main
```
