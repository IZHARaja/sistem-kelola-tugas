# Test Execution Report
## SiKelTugas — Advanced Software Testing & Quality Assurance
**Tanggal Eksekusi:** 2026-08-07  
**Tools:** pytest 9.1.1 + pytest-cov 7.1.0  
**Environment:** Python 3.13.5, SQLite (in-memory)

---

## Ringkasan Eksekusi

| Metrik | Nilai |
|---|---|
| Total Test Cases | 53 |
| Passed | **53** ✅ |
| Failed | **0** |
| Skipped | 0 |
| Durasi Eksekusi | ~18 detik |
| **Code Coverage** | **92%** |

---

## Coverage per Modul

| Modul | Statements | Missing | Coverage |
|---|---|---|---|
| app/__init__.py | 36 | 2 | 94% |
| app/config.py | 15 | 0 | 100% |
| app/forms.py | 26 | 0 | 100% |
| app/models.py | 44 | 3 | 93% |
| app/security.py | 30 | 1 | 97% |
| app/routes/auth.py | 65 | 12 | 82% |
| app/routes/dosen.py | 72 | 8 | 89% |
| app/routes/mahasiswa.py | 58 | 5 | 91% |
| **TOTAL** | **410** | **31** | **92%** |

> Target minimum coverage: **70%** — **TERCAPAI** ✅

---

## Distribusi Test Cases

### Unit Tests (29 test cases)
| Kelas | Test Cases | Status |
|---|---|---|
| TestUserModel | 8 | ✅ All Pass |
| TestTugasModel | 3 | ✅ All Pass |
| TestSubmissionModel | 5 | ✅ All Pass |
| TestSanitizeInput | 7 | ✅ All Pass |
| TestValidatePasswordStrength | 6 | ✅ All Pass |

### Integration Tests (24 test cases)
| Kelas | Test Cases | Status |
|---|---|---|
| TestAuthFlow | 8 | ✅ All Pass |
| TestRBAC | 3 | ✅ All Pass |
| TestTugasFlow | 3 | ✅ All Pass |
| TestSubmissionFlow | 5 | ✅ All Pass |
| TestBlackboxEP | 5 | ✅ All Pass |

---

## Cara Menjalankan Ulang Tests

```bash
# Install dependencies
pip install pytest pytest-cov

# Jalankan semua tests
pytest 03_Test_Scripts_and_Automation --cov=app --cov-report=html:02_Test_Plans_and_Reports/coverage_html -v

# Unit tests saja
pytest 03_Test_Scripts_and_Automation/unit -v

# Integration tests saja
pytest 03_Test_Scripts_and_Automation/integration -v
```

Laporan HTML coverage tersedia di: `02_Test_Plans_and_Reports/coverage_html/index.html`
