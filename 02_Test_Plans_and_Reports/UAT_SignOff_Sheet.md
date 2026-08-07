# UAT Sign-off Sheet
## SiKelTugas — User Acceptance Testing
**Tanggal UAT:** ________________  
**Versi Aplikasi:** 2.0  
**Environment:** Production / Staging  
**URL Aplikasi:** https://sistem-kelola-tugas.vercel.app

---

## Informasi Peserta UAT

| Peran | Nama | Jabatan | Tanda Tangan |
|---|---|---|---|
| End User (Dosen) | ________________ | Dosen/Pengajar | ________________ |
| End User (Mahasiswa) | ________________ | Mahasiswa | ________________ |
| QA Lead | ________________ | Quality Assurance | ________________ |
| Product Owner | ________________ | Pengembang | ________________ |

---

## Skenario Pengujian UAT

### Modul 1: Autentikasi & Akun

| ID | Skenario | Langkah | Kriteria Penerimaan | Hasil | Catatan |
|---|---|---|---|---|---|
| UAT-01 | Registrasi Dosen | 1. Buka /register<br>2. Isi form dengan role Dosen<br>3. Submit | Akun terdaftar, redirect ke /login, flash message "Akun berhasil dibuat" | PASS / FAIL | |
| UAT-02 | Registrasi Mahasiswa | 1. Buka /register<br>2. Isi form dengan role Mahasiswa<br>3. Submit | Akun terdaftar, redirect ke /login | PASS / FAIL | |
| UAT-03 | Login Valid | 1. Buka /login<br>2. Masukkan kredensial benar<br>3. Submit | Redirect ke dashboard sesuai role | PASS / FAIL | |
| UAT-04 | Login Invalid | 1. Masukkan password salah<br>2. Submit | Pesan error "Username atau password salah", tidak ada redirect | PASS / FAIL | |
| UAT-05 | Password Lemah | 1. Coba register dengan "password123"<br>2. Submit | Form ditolak dengan pesan error kekuatan password | PASS / FAIL | |
| UAT-06 | Logout | 1. Login<br>2. Klik tombol Logout | Sesi dihapus, redirect ke /login | PASS / FAIL | |

### Modul 2: Manajemen Tugas (Dosen)

| ID | Skenario | Langkah | Kriteria Penerimaan | Hasil | Catatan |
|---|---|---|---|---|---|
| UAT-07 | Buat Tugas Baru | 1. Login sebagai Dosen<br>2. Klik "Buat Tugas"<br>3. Isi judul, deskripsi, deadline<br>4. Submit | Tugas muncul di dashboard, flash "Tugas berhasil dibuat" | PASS / FAIL | |
| UAT-08 | Edit Tugas | 1. Klik tombol Edit pada tugas<br>2. Ubah judul<br>3. Submit | Judul berubah di dashboard | PASS / FAIL | |
| UAT-09 | Hapus Tugas | 1. Klik tombol Hapus pada tugas<br>2. Konfirmasi | Tugas hilang dari dashboard | PASS / FAIL | |
| UAT-10 | Lihat Submissions | 1. Klik "Lihat Submission" pada tugas<br>2. Observasi tabel | Menampilkan daftar mahasiswa yang mengumpulkan beserta file/link | PASS / FAIL | |
| UAT-11 | IDOR Protection | 1. Copy URL tugas milik dosen lain<br>2. Akses langsung | Halaman 404 muncul, tugas tidak dapat diakses | PASS / FAIL | |

### Modul 3: Pengumpulan Tugas (Mahasiswa)

| ID | Skenario | Langkah | Kriteria Penerimaan | Hasil | Catatan |
|---|---|---|---|---|---|
| UAT-12 | Submit Teks | 1. Login sebagai Mahasiswa<br>2. Klik "Kumpulkan" pada tugas<br>3. Isi textarea<br>4. Submit | Submission tersimpan, status "Sudah Dikumpulkan" di dashboard | PASS / FAIL | |
| UAT-13 | Submit File | 1. Klik "Kumpulkan"<br>2. Upload file PDF<br>3. Submit | File tersimpan, dapat diunduh oleh dosen | PASS / FAIL | |
| UAT-14 | Submit Link URL | 1. Klik "Kumpulkan"<br>2. Masukkan URL Google Drive<br>3. Submit | URL tersimpan, dapat dibuka oleh dosen | PASS / FAIL | |
| UAT-15 | Submit Kosong | 1. Submit form tanpa isi apapun | Error: "Isi minimal salah satu: teks, file, atau link" | PASS / FAIL | |
| UAT-16 | Double Submit | 1. Submit tugas<br>2. Coba submit ulang untuk tugas yang sama | Flash warning "Anda sudah mengumpulkan tugas ini", redirect ke dashboard | PASS / FAIL | |
| UAT-17 | Submit Setelah Deadline | 1. Coba submit tugas dengan deadline lampau | Flash error, submit diblokir | PASS / FAIL | |

### Modul 4: Keamanan & Tampilan

| ID | Skenario | Langkah | Kriteria Penerimaan | Hasil | Catatan |
|---|---|---|---|---|---|
| UAT-18 | RBAC — Mahasiswa ke Dosen | 1. Login sebagai Mahasiswa<br>2. Akses /dosen/dashboard | Halaman 403 Forbidden | PASS / FAIL | |
| UAT-19 | Tampilan Responsif | 1. Buka di mobile (320px)<br>2. Observasi layout | Layout tidak rusak, semua elemen terbaca | PASS / FAIL | |
| UAT-20 | Flash Messages | 1. Lakukan aksi sukses/gagal<br>2. Observasi notifikasi | Pesan flash muncul dengan warna sesuai (hijau=sukses, merah=error) | PASS / FAIL | |

---

## Ringkasan Hasil UAT

| Metrik | Nilai |
|---|---|
| Total Skenario | 20 |
| PASS | ___ |
| FAIL | ___ |
| Persentase Keberhasilan | ___% |
| Status Penerimaan | ☐ DITERIMA &nbsp;&nbsp; ☐ DITOLAK &nbsp;&nbsp; ☐ BERSYARAT |

---

## Daftar Defect Ditemukan

| ID Defect | Skenario Terkait | Deskripsi | Tingkat Keparahan | Status |
|---|---|---|---|---|
| DEF-001 | | | Critical / High / Medium / Low | Open / Fixed |

---

## Pernyataan Sign-off

Dengan menandatangani dokumen ini, semua pihak menyatakan bahwa pengujian telah dilaksanakan sesuai skenario dan hasilnya telah diverifikasi.

**Diterima / Ditolak:** ________________

| Peran | Nama | Tanda Tangan | Tanggal |
|---|---|---|---|
| End User (Dosen) | | | |
| End User (Mahasiswa) | | | |
| QA Lead | | | |
| Product Owner | | | |
