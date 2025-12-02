// ===== CONFIGURAÇÕES =====

// Verificar autenticação
if (!TokenManager.isAuthenticated()) {
    window.location.href = '/';
}

// ===== DARK MODE =====
const DARK_MODE_KEY = 'darkMode';

// Carregar preferência salva
function carregarDarkMode() {
    const darkMode = localStorage.getItem(DARK_MODE_KEY) === 'true';
    const toggle = document.getElementById('darkModeToggle');
    
    if (darkMode) {
        document.body.classList.add('dark-mode');
        if (toggle) toggle.checked = true;
    }
}

// Toggle dark mode
function toggleDarkMode() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem(DARK_MODE_KEY, isDark);
}

// Event listener do toggle
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('change', toggleDarkMode);
}

// ===== CARREGAR DADOS DO USUÁRIO =====
async function carregarUsuario() {
    const usuario = await AuthAPI.getMe();
    if (usuario) {
        document.getElementById('userName').textContent = usuario.first_name || usuario.username;
        document.getElementById('userEmail').textContent = usuario.email || 'Sem e-mail';
    }
}

// ===== LOGOUT =====
function logout() {
    if (confirm('Deseja realmente sair?')) {
        AuthAPI.logout();
    }
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
    carregarDarkMode();
    carregarUsuario();
});