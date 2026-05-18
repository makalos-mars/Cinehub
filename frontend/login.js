// autenticación conectada a PostgreSQL vía FastAPI

const API = 'http://localhost:8000';

// ── UTILIDADES ──
const $ = id => document.getElementById(id);

function setError(fieldId, message) {
  const el = $(fieldId);
  if (el) el.textContent = message;
}
function clearError(fieldId) { setError(fieldId, ''); }

function setInputState(inputEl, state) {
  const wrap = inputEl.closest('.input-wrap');
  if (!wrap) return;
  wrap.classList.remove('error', 'success');
  if (state) wrap.classList.add(state);
}

function showMessage(elId, message, type) {
  const el = $(elId);
  if (!el) return;
  el.textContent = message;
  el.className = 'auth-message ' + (type === 'success' ? 'success-msg' : 'error-msg');
}
function clearMessage(elId) {
  const el = $(elId);
  if (el) { el.textContent = ''; el.className = 'auth-message'; }
}

function setLoading(formType, loading) {
  const btn = $(formType === 'login' ? 'loginBtn' : 'registerBtn');
  const text = btn.querySelector('.btn-text');
  const loader = btn.querySelector('.btn-loader');
  btn.disabled = loading;
  text.style.display = loading ? 'none' : '';
  loader.style.display = loading ? 'flex' : 'none';
}

// ── TABS ──
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === target));
    $('loginForm').classList.toggle('hidden', target !== 'login');
    $('registerForm').classList.toggle('hidden', target !== 'register');
    clearMessage('loginMessage');
    clearMessage('registerMessage');
  });
});

// ── TOGGLE CONTRASEÑA ──
document.querySelectorAll('.toggle-pwd').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = $(btn.dataset.target);
    const isText = input.type === 'text';
    input.type = isText ? 'password' : 'text';
    btn.querySelector('.eye-open').style.display = isText ? '' : 'none';
    btn.querySelector('.eye-closed').style.display = isText ? 'none' : '';
  });
});

// ── BOTONES DEMO ──
document.querySelectorAll('.demo-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    $('loginEmail').value = btn.dataset.email;
    $('loginPassword').value = btn.dataset.pwd;
    ['loginEmail', 'loginPassword'].forEach(id => {
      clearError(id + 'Error');
      setInputState($(id), '');
    });
    clearMessage('loginMessage');
  });
});

// ── VERIFICACIÓN DE EMAIL EN TIEMPO REAL (Registro) ──
let emailCheckTimeout = null;

$('regEmail').addEventListener('input', function () {
  clearTimeout(emailCheckTimeout);
  const email = this.value.trim();
  const statusEl = $('emailStatus');

  clearError('regEmailError');
  setInputState(this, '');
  statusEl.textContent = '';

  if (!email) return;

  emailCheckTimeout = setTimeout(async () => {
    if (!isValidEmail(email)) {
      setInputState($('regEmail'), 'error');
      setError('regEmailError', 'Ingresa un correo electrónico válido.');
      statusEl.textContent = '✗';
      statusEl.style.color = 'var(--error)';
      return;
    }

    statusEl.textContent = '...';
    statusEl.style.color = 'var(--muted)';

    try {
      const res = await fetch(`${API}/api/auth/verificar-correo/${encodeURIComponent(email)}`);
      const data = await res.json();
      if (data.existe) {
        setInputState($('regEmail'), 'error');
        setError('regEmailError', 'Este correo ya está registrado. ¿Quieres iniciar sesión?');
        statusEl.textContent = '✗';
        statusEl.style.color = 'var(--error)';
      } else {
        setInputState($('regEmail'), 'success');
        statusEl.textContent = '✓';
        statusEl.style.color = 'var(--success)';
      }
    } catch {
      statusEl.textContent = '';
    }
  }, 500);
});

// ── MEDIDOR DE CONTRASEÑA ──
$('regPassword').addEventListener('input', function () {
  updateStrengthMeter(this.value);
});

function updateStrengthMeter(pwd) {
  const bars = ['bar1', 'bar2', 'bar3', 'bar4'].map(id => $(id));
  const label = $('strengthLabel');
  bars.forEach(b => { b.className = 'bar'; });

  if (!pwd) { label.textContent = 'Sin contraseña'; return; }

  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;

  const configs = [
    { color: 'weak',   text: 'Muy débil' },
    { color: 'weak',   text: 'Débil' },
    { color: 'medium', text: 'Media' },
    { color: 'medium', text: 'Buena' },
    { color: 'strong', text: 'Fuerte' },
  ];
  const cfg = configs[score] || configs[0];
  label.textContent = cfg.text;
  for (let i = 0; i < score; i++) bars[i].classList.add(cfg.color);
}

// ── VALIDACIONES ──
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateLoginForm() {
  let valid = true;
  const email = $('loginEmail').value.trim();
  const pwd = $('loginPassword').value;

  clearError('loginEmailError');
  clearError('loginPasswordError');
  setInputState($('loginEmail'), '');
  setInputState($('loginPassword'), '');

  if (!email) {
    setError('loginEmailError', 'El correo es obligatorio.');
    setInputState($('loginEmail'), 'error');
    valid = false;
  } else if (!isValidEmail(email)) {
    setError('loginEmailError', 'Ingresa un correo válido.');
    setInputState($('loginEmail'), 'error');
    valid = false;
  }

  if (!pwd) {
    setError('loginPasswordError', 'La contraseña es obligatoria.');
    setInputState($('loginPassword'), 'error');
    valid = false;
  }

  return valid;
}

function validateRegisterForm() {
  let valid = true;
  const name = $('regName').value.trim();
  const lastName = $('regLastName').value.trim();
  const email = $('regEmail').value.trim();
  const pwd = $('regPassword').value;
  const role = document.querySelector('input[name="userRole"]:checked')?.value;

  ['regNameError', 'regLastNameError', 'regEmailError', 'regPasswordError', 'regRoleError']
    .forEach(clearError);
  [$('regName'), $('regLastName'), $('regEmail'), $('regPassword')]
    .forEach(el => setInputState(el, ''));

  if (!name) {
    setError('regNameError', 'El nombre es obligatorio.');
    setInputState($('regName'), 'error');
    valid = false;
  }
  if (!lastName) {
    setError('regLastNameError', 'El apellido es obligatorio.');
    setInputState($('regLastName'), 'error');
    valid = false;
  }
  if (!email) {
    setError('regEmailError', 'El correo es obligatorio.');
    setInputState($('regEmail'), 'error');
    valid = false;
  } else if (!isValidEmail(email)) {
    setError('regEmailError', 'Ingresa un correo válido.');
    setInputState($('regEmail'), 'error');
    valid = false;
  }
  if (!pwd) {
    setError('regPasswordError', 'La contraseña es obligatoria.');
    setInputState($('regPassword'), 'error');
    valid = false;
  } else if (pwd.length < 8) {
    setError('regPasswordError', 'Mínimo 8 caracteres.');
    setInputState($('regPassword'), 'error');
    valid = false;
  }
  if (!role) {
    setError('regRoleError', 'Selecciona tu rol en CineHub.');
    valid = false;
  }

  return valid;
}

// ── MENSAJES DE BIENVENIDA POR ROL ──
const ROLE_MESSAGES = {
  aficionado: { title: '¡Bienvenido, Aficionado!', desc: 'Disfruta tus recomendaciones personalizadas.' },
  critico:    { title: '¡Hola, Crítico!',          desc: 'Tus reseñas esperan ser escritas.' },
  reportero:  { title: '¡Listo, Reportero!',       desc: 'Cubre los últimos estrenos del cine mexicano.' },
  director:   { title: '¡Bienvenido, Director!',   desc: 'Gestiona tus producciones desde el panel.' },
};

function showSuccessModal(user) {
  const msg = ROLE_MESSAGES[user.role] || { title: '¡Bienvenido!', desc: 'Redirigiendo...' };
  $('successTitle').textContent = msg.title;
  $('successDesc').textContent = msg.desc;

  sessionStorage.setItem('cinehub_session', JSON.stringify({
    nombre: user.nombre,
    correo: user.correo,
    role: user.role,
  }));

  window.location.href = 'dashboard.html';
}

// ── SUBMIT LOGIN ──
$('loginForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  clearMessage('loginMessage');
  if (!validateLoginForm()) return;

  setLoading('login', true);

  const correo = $('loginEmail').value.trim();
  const contrasena = $('loginPassword').value;

  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, contrasena })
    });
    const data = await res.json();
    setLoading('login', false);

    if (!data.ok) {
      showMessage('loginMessage', data.mensaje || 'Correo o contraseña incorrectos.', 'error');
      setInputState($('loginEmail'), 'error');
      setInputState($('loginPassword'), 'error');
      $('loginBtn').classList.add('shake');
      setTimeout(() => $('loginBtn').classList.remove('shake'), 500);
      return;
    }

    showSuccessModal({ nombre: data.nombre, correo: data.correo, role: data.rol });
  } catch {
    setLoading('login', false);
    showMessage('loginMessage', 'No se pudo conectar con el servidor. ¿Está corriendo el backend?', 'error');
  }
});

// ── SUBMIT REGISTRO ──
$('registerForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  clearMessage('registerMessage');
  if (!validateRegisterForm()) return;

  setLoading('register', true);

  const nombre = $('regName').value.trim();
  const apellido = $('regLastName').value.trim();
  const correo = $('regEmail').value.trim();
  const contrasena = $('regPassword').value;
  const rol = document.querySelector('input[name="userRole"]:checked').value;

  try {
    const res = await fetch(`${API}/api/auth/registro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, apellido, correo, contrasena, rol })
    });
    const data = await res.json();
    setLoading('register', false);

    if (!data.ok) {
      if (data.mensaje?.includes('correo')) {
        setError('regEmailError', data.mensaje);
        setInputState($('regEmail'), 'error');
      } else {
        showMessage('registerMessage', data.mensaje || 'Error al crear la cuenta.', 'error');
      }
      return;
    }

    showSuccessModal({ nombre: data.nombre, correo: data.correo, role: data.rol });
  } catch {
    setLoading('register', false);
    showMessage('registerMessage', 'No se pudo conectar con el servidor. ¿Está corriendo el backend?', 'error');
  }
});

// ── INICIALIZACIÓN ──
(function checkSession() {
  if (sessionStorage.getItem('cinehub_session')) {
    window.location.href = 'dashboard.html';
  }
})();
