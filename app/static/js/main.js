'use strict';

function updateRoleButtons(groupName, role) {
    document.querySelectorAll('[data-role-switch="' + groupName + '"] [data-role-option]').forEach(function (button) {
        button.classList.toggle('active', button.dataset.roleOption === role);
    });
}

function bindRoleButtons(groupName, selectId, syncFn) {
    const switcher = document.querySelector('[data-role-switch="' + groupName + '"]');
    const roleField = document.getElementById(selectId);

    if (!switcher || !roleField) {
        return;
    }

    switcher.querySelectorAll('[data-role-option]').forEach(function (button) {
        button.addEventListener('click', function () {
            roleField.value = button.dataset.roleOption;
            syncFn();
        });
    });

    roleField.addEventListener('change', syncFn);
}

function syncLoginRole() {
    const roleField = document.getElementById('role');
    if (!roleField || !document.querySelector('[data-role-switch="login"]')) {
        return;
    }

    const role = roleField.value === 'dosen' ? 'dosen' : 'mahasiswa';
    const identifierLabel = document.getElementById('identifierLabel');
    const identifierInput = document.getElementById('identifier');
    const identifierHelp = document.getElementById('identifierHelp');
    const roleTitle = document.getElementById('loginRoleTitle');
    const roleHint = document.getElementById('loginRoleHint');
    const roleIcon = document.getElementById('loginRoleIcon');
    const roleIconWrap = document.getElementById('loginRoleIconWrap');
    const fullNameHelp = document.getElementById('fullNameHelp');

    updateRoleButtons('login', role);

    if (identifierLabel) {
        identifierLabel.innerHTML = role === 'dosen'
            ? '<i class="fas fa-id-card"></i> NIP'
            : '<i class="fas fa-id-card"></i> NIS';
    }

    if (identifierInput) {
        identifierInput.placeholder = role === 'dosen'
            ? 'Masukkan NIP yang terdaftar'
            : 'Masukkan NIS yang terdaftar';
    }

    if (identifierHelp) {
        identifierHelp.textContent = role === 'dosen'
            ? 'Gunakan NIP yang sudah tersimpan di sistem sekolah.'
            : 'Gunakan NIS yang sudah tersimpan di sistem.';
    }

    if (roleTitle) {
        roleTitle.textContent = role === 'dosen'
            ? 'Portal Guru'
            : 'Portal Siswa';
    }

    if (roleHint) {
        roleHint.textContent = role === 'dosen'
            ? 'Masuk memakai NIP, email aktif, nama lengkap, dan password akun pengajar.'
            : 'Masuk memakai NIS, email aktif, nama lengkap, dan password akun belajar.';
    }

    if (roleIcon) {
        roleIcon.className = role === 'dosen' ? 'fas fa-chalkboard-teacher' : 'fas fa-user-graduate';
    }

    if (roleIconWrap) {
        roleIconWrap.classList.toggle('teacher-mode', role === 'dosen');
    }

    if (fullNameHelp) {
        fullNameHelp.textContent = role === 'dosen'
            ? 'Tuliskan nama lengkap sesuai data pegawai yang terdaftar.'
            : 'Tuliskan nama lengkap persis seperti data akademik yang terdaftar.';
    }
}

function syncRegisterRole() {
    const roleField = document.getElementById('role');
    if (!roleField || !document.querySelector('[data-role-switch="register"]')) {
        return;
    }

    const role = roleField.value === 'dosen' ? 'dosen' : 'mahasiswa';
    const nisGroup = document.getElementById('nisGroup');
    const nipGroup = document.getElementById('nipGroup');
    const roleTitle = document.getElementById('registerRoleTitle');
    const roleHint = document.getElementById('registerRoleHint');
    const roleIcon = document.getElementById('registerRoleIcon');
    const roleIconWrap = document.getElementById('registerRoleIconWrap');

    updateRoleButtons('register', role);

    if (nisGroup) {
        nisGroup.classList.toggle('form-group-hidden', role === 'dosen');
    }

    if (nipGroup) {
        nipGroup.classList.toggle('form-group-hidden', role !== 'dosen');
    }

    if (roleTitle) {
        roleTitle.textContent = role === 'dosen'
            ? 'Pendaftaran Guru'
            : 'Pendaftaran Siswa';
    }

    if (roleHint) {
        roleHint.textContent = role === 'dosen'
            ? 'Siapkan nama lengkap, email aktif, NIP, dan password yang kuat.'
            : 'Siapkan nama lengkap, email aktif, NIS, dan password yang kuat.';
    }

    if (roleIcon) {
        roleIcon.className = role === 'dosen' ? 'fas fa-chalkboard-teacher' : 'fas fa-user-graduate';
    }

    if (roleIconWrap) {
        roleIconWrap.classList.toggle('teacher-mode', role === 'dosen');
    }
}

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
    document.body.classList.add('js-ready');

    syncLoginRole();
    syncRegisterRole();

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
