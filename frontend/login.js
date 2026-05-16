
// autenticación con roles y validaciones


// ── BASE DE DATOS SIMULADA 
const DB_USERS = [
  { id: 1, name: 'Carlos', lastName: 'Mendoza', email: 'aficionado@cinehub.mx', password: 'test1234', role: 'aficionado' },
  { id: 2, name: 'Alejandra', lastName: 'Ríos', email: 'critico@cinehub.mx', password: 'test1234', role: 'critico' },
  { id: 3, name: 'Roberto', lastName: 'Salinas', email: 'reportero@cinehub.mx', password: 'test1234', role: 'reportero' },
  { id: 4, name: 'Patricia', lastName: 'Vega', email: 'director@cinehub.mx', password: 'test1234', role: 'director' },
];

// Registros guardados en sessionStorage
function getRegisteredUsers() {
  try { return JSON.parse(sessionStorage.getItem('cinehub_users') || '[]'); }
  catch { return []; }
}
function saveRegisteredUsers(users) {
  sessionStorage.setItem('cinehub_users', JSON.stringify(users));
}
function getAllUsers() {
  return [...DB_USERS, ...getRegisteredUsers()];
}

// ── UTILIDADES ──
const $ = id => document.getElementById(id);

function setError(fieldId, message) {
  const el = $(fieldId);
  if (el) el.textContent = message;
}
function clearError(fieldId) { setError(fieldId, ''); }

function setInputState(inputEl, state) {
  // state: 'error' | 'success' | ''
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

function simulateDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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
    // Limpiar errores previos
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

  // Esperar 500ms para no verificar con cada tecla
  emailCheckTimeout = setTimeout(() => {
    if (!isValidEmail(email)) {
      setInputState($('regEmail'), 'error');
      setError('regEmailError', 'Ingresa un correo electrónico válido.');
      statusEl.textContent = '✗';
      statusEl.style.color = 'var(--error)';
      return;
    }

    // Simular verificación contra la base de datos
    statusEl.style.color = 'var(--muted)';

    setTimeout(() => {
      const exists = getAllUsers().some(u => u.email.toLowerCase() === email.toLowerCase());
      if (exists) {
        setInputState($('regEmail'), 'error');
        setError('regEmailError', 'Este correo ya está registrado. ¿Quieres iniciar sesión?');
        statusEl.textContent = '✗';
        statusEl.style.color = 'var(--error)';
      } else {
        setInputState($('regEmail'), 'success');
        statusEl.textContent = '✓';
        statusEl.style.color = 'var(--success)';
      }
    }, 400);
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
    { color: 'weak', text: 'Muy débil' },
    { color: 'weak', text: 'Débil' },
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
  } else {
    const exists = getAllUsers().some(u => u.email.toLowerCase() === email.toLowerCase());
    if (exists) {
      setError('regEmailError', 'Este correo ya está registrado.');
      setInputState($('regEmail'), 'error');
      valid = false;
    }
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

// ── LÓGICA DE AUTENTICACIÓN ──

// Mensajes de bienvenida por rol
const ROLE_MESSAGES = {
  aficionado: { title: '¡Bienvenido, Aficionado!', desc: 'Disfruta tus recomendaciones personalizadas.' },
  critico: { title: '¡Hola, Crítico!', desc: 'Tus reseñas esperan ser escritas.' },
  reportero: { title: '¡Listo, Reportero!', desc: 'Cubre los últimos estrenos del cine mexicano.' },
  director: { title: '¡Bienvenido, Director!', desc: 'Gestiona tus producciones desde el panel.' },
};

function showSuccessModal(user) {
  const modal = $('successModal');
  const title = $('successTitle');
  const desc = $('successDesc');
  const fill = $('progressFill');
  const msg = ROLE_MESSAGES[user.role] || { title: '¡Bienvenido!', desc: 'Redirigiendo...' };

  title.textContent = msg.title;
  desc.textContent = msg.desc;
  fill.style.width = '0%';

  // modal.classList.add('open');

  // Guardar sesión en sessionStorage
  sessionStorage.setItem('cinehub_session', JSON.stringify({
    id: user.id,
    name: user.name,
    lastName: user.lastName,
    email: user.email,
    role: user.role,
  }));

  // // Animación de progreso → redirigir
  // requestAnimationFrame(() => {
  //   requestAnimationFrame(() => { fill.style.width = '100%'; });
  // });

  // setTimeout(() => {
  //   window.location.href = 'dashboard.html';
  // }, 2800);
  window.location.href = 'dashboard.html';
}

// ── SUBMIT LOGIN ──
$('loginForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  clearMessage('loginMessage');
  if (!validateLoginForm()) return;

  setLoading('login', true);
  // await simulateDelay(900); // Simula latencia del servidor

  const email = $('loginEmail').value.trim().toLowerCase();
  const pwd = $('loginPassword').value;

  const user = getAllUsers().find(
    u => u.email.toLowerCase() === email && u.password === pwd
  );

  setLoading('login', false);

  if (!user) {
    showMessage('loginMessage', 'Correo o contraseña incorrectos. Verifica tus datos.', 'error');
    setInputState($('loginEmail'), 'error');
    setInputState($('loginPassword'), 'error');
    // Sacudir el botón
    $('loginBtn').classList.add('shake');
    setTimeout(() => $('loginBtn').classList.remove('shake'), 500);
    return;
  }

  showSuccessModal(user);
});

// ── SUBMIT REGISTRO ──
$('registerForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  clearMessage('registerMessage');
  if (!validateRegisterForm()) return;

  setLoading('register', true);
  await simulateDelay(1100);

  const name = $('regName').value.trim();
  const lastName = $('regLastName').value.trim();
  const email = $('regEmail').value.trim();
  const pwd = $('regPassword').value;
  const role = document.querySelector('input[name="userRole"]:checked').value;

  // Volver a verificar por si acaso
  const emailTaken = getAllUsers().some(u => u.email.toLowerCase() === email.toLowerCase());
  if (emailTaken) {
    setLoading('register', false);
    setError('regEmailError', 'Este correo ya está registrado.');
    setInputState($('regEmail'), 'error');
    return;
  }

  // Crear usuario
  const newUser = {
    id: Date.now(),
    name, lastName, email,
    password: pwd,
    role,
  };

  const registered = getRegisteredUsers();
  registered.push(newUser);
  saveRegisteredUsers(registered);

  setLoading('register', false);
  showSuccessModal(newUser);
});

// ── INICIALIZACIÓN ──
(function checkSession() {
  const session = sessionStorage.getItem('cinehub_session');
  if (session) {
    window.location.href = 'dashboard.html';
  }
})();
