// Toggle sidebar collapse
const toggleBtn = document.getElementById('sidebarToggle');
const sidebar   = document.getElementById('sidebar');

if (toggleBtn && sidebar) {
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('show');
  });
}

// Auto-dismiss alerts after 4 seconds
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(el => {
    try { bootstrap.Alert.getOrCreateInstance(el).close(); } catch {}
  });
}, 4000);

// Highlight active sidebar link
document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
  const href = link.getAttribute('href');
  if (href && href !== '/' && window.location.pathname.startsWith(href)) {
    link.classList.add('active');
  }
});

// Theme Management
const themeToggle = document.getElementById('themeToggle');
const themeToggleIcon = document.getElementById('themeToggleIcon');

function getTheme() {
  return localStorage.getItem('theme') || 'light';
}

function setTheme(theme) {
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);
}

function updateThemeIcon(theme) {
  if (!themeToggleIcon) return;
  if (theme === 'dark') {
    themeToggleIcon.className = 'bi bi-sun-fill';
  } else {
    themeToggleIcon.className = 'bi bi-moon-stars';
  }
}

// Initialize icon on page load
if (themeToggleIcon) {
  updateThemeIcon(getTheme());
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const currentTheme = getTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  });
}
