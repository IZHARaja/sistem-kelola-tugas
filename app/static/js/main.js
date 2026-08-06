'use strict';

/* ── Toggle show/hide password ─────────────────────────── */
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const eye   = document.getElementById('eye-' + fieldId);
    if (!field || !eye) return;
    if (field.type === 'password') {
        field.type = 'text';
        eye.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        field.type = 'password';
        eye.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

/* ── Konfirmasi hapus tugas ─────────────────────────────── */
function confirmDelete(name) {
    return window.confirm(
        'Hapus tugas "' + name + '"?\n\nSeluruh submission yang terkait juga akan ikut terhapus.'
    );
}

/* ── Password strength meter ────────────────────────────── */
function calcStrength(pw) {
    let score = 0;
    if (pw.length >= 8)            score++;
    if (pw.length >= 12)           score++;
    if (/[A-Z]/.test(pw))          score++;
    if (/[a-z]/.test(pw))          score++;
    if (/\d/.test(pw))             score++;
    if (/[^A-Za-z0-9]/.test(pw))   score++;
    return Math.min(Math.floor(score * 5 / 6), 4);
}

const STRENGTH_LEVELS = [
    { pct: 20,  color: '#f5365c', label: 'Sangat Lemah' },
    { pct: 40,  color: '#fb6340', label: 'Lemah' },
    { pct: 65,  color: '#ffd600', label: 'Sedang' },
    { pct: 85,  color: '#2dce89', label: 'Kuat' },
    { pct: 100, color: '#11cdef', label: 'Sangat Kuat' },
];

document.addEventListener('DOMContentLoaded', function () {
    /* Password strength on register page */
    const pwField      = document.getElementById('password');
    const strengthDiv  = document.getElementById('passwordStrength');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    if (pwField && strengthDiv) {
        strengthDiv.style.display = 'none';

        pwField.addEventListener('input', function () {
            const val = pwField.value;
            if (!val) {
                strengthDiv.style.display = 'none';
                return;
            }
            strengthDiv.style.display = 'block';
            const level = STRENGTH_LEVELS[calcStrength(val)];
            strengthFill.style.width      = level.pct + '%';
            strengthFill.style.background = level.color;
            strengthText.textContent      = level.label;
            strengthText.style.color      = level.color;
        });
    }

    /* Auto-dismiss flash messages setelah 5 detik */
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity    = '0';
            alert.style.transform  = 'translateY(-8px)';
            setTimeout(function () { alert.remove(); }, 500);
        }, 5000);
    });
});
