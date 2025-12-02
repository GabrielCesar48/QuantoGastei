// ===== DARK MODE GLOBAL =====
// Este código deve ser executado em TODAS as páginas

(function() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
})();