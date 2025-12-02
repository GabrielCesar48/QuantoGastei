// ===== ONBOARDING - SISTEMA DE BOAS-VINDAS =====

// Aplicar dark mode imediatamente
const darkMode = localStorage.getItem('darkMode') === 'true';
if (darkMode) {
    document.body.classList.add('dark-mode');
}

// ===== DADOS DO USUÁRIO (LOCAL STORAGE) =====
const UserData = {
    save(data) {
        const current = this.get() || {};
        const updated = { ...current, ...data };
        localStorage.setItem('userData', JSON.stringify(updated));
    },
    
    get() {
        const data = localStorage.getItem('userData');
        return data ? JSON.parse(data) : null;
    },
    
    clear() {
        localStorage.removeItem('userData');
    },
    
    isOnboardingComplete() {
        return localStorage.getItem('onboardingComplete') === 'true';
    },
    
    setOnboardingComplete() {
        localStorage.setItem('onboardingComplete', 'true');
    }
};

// ===== WELCOME PAGE (STEP 1) =====
function proximoPasso() {
    const nome = document.getElementById('nome');
    
    if (!nome) {
        window.location.href = '/onboarding/step2/';
        return;
    }
    
    if (!nome.value.trim()) {
        alert('Por favor, digite seu nome');
        nome.focus();
        return;
    }
    
    UserData.save({
        nome: nome.value.trim(),
        dataRegistro: new Date().toISOString()
    });
    
    window.location.href = '/onboarding/step2/';
}

function pularOnboarding() {
    UserData.save({
        nome: 'Usuário',
        dataRegistro: new Date().toISOString()
    });
    UserData.setOnboardingComplete();
    window.location.href = '/home/';
}

function loginComGoogle() {
    window.location.href = '/auth/google/';
}

// ===== STEP 2 (TELEFONE E PREFERÊNCIAS) =====
if (document.getElementById('telefone')) {
    const telefoneInput = document.getElementById('telefone');
    const darkModeToggle = document.getElementById('darkMode');
    const notificacoesToggle = document.getElementById('notificacoes');
    
    // Aplicar máscara de telefone
    telefoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        if (value.length <= 11) {
            if (value.length <= 2) {
                value = value.replace(/^(\d{0,2})/, '($1');
            } else if (value.length <= 6) {
                value = value.replace(/^(\d{2})(\d{0,4})/, '($1) $2');
            } else if (value.length <= 10) {
                value = value.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else {
                value = value.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
            }
        }
        
        e.target.value = value;
    });
    
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    darkModeToggle.checked = savedDarkMode;
    
    window.voltarPasso = function() {
        window.location.href = '/onboarding/welcome/';
    };
    
    window.proximoPasso = function() {
        const telefone = telefoneInput.value.replace(/\D/g, '');
        const darkMode = darkModeToggle.checked;
        const notificacoes = notificacoesToggle.checked;
        
        UserData.save({
            telefone: telefone || null,
            darkMode: darkMode,
            notificacoes: notificacoes
        });
        
        localStorage.setItem('darkMode', darkMode);
        
        window.location.href = '/onboarding/tutorial/';
    };
}

// ===== STEP 3 (TUTORIAL SLIDER) =====
if (document.getElementById('tutorialSlider')) {
    let slideAtual = 0;
    const slides = document.querySelectorAll('.tutorial-slide');
    const dots = document.querySelectorAll('.dot');
    const btnAvancar = document.getElementById('btnAvancar');
    
    function mostrarSlide(index) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        
        slideAtual = index;
        
        if (index === slides.length - 1) {
            btnAvancar.innerHTML = `
                Começar
                <span class="material-symbols-outlined">check</span>
            `;
        } else {
            btnAvancar.innerHTML = `
                Próximo
                <span class="material-symbols-outlined">arrow_forward</span>
            `;
        }
    }
    
    window.irParaSlide = function(index) {
        if (index >= 0 && index < slides.length) {
            mostrarSlide(index);
        }
    };
    
    window.voltarSlide = function() {
        if (slideAtual > 0) {
            mostrarSlide(slideAtual - 1);
        } else {
            window.location.href = '/onboarding/step2/';
        }
    };
    
    window.avancarSlide = function() {
        if (slideAtual < slides.length - 1) {
            mostrarSlide(slideAtual + 1);
        } else {
            UserData.setOnboardingComplete();
            window.location.href = '/home/';
        }
    };
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    const slider = document.getElementById('tutorialSlider');
    slider.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    slider.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        if (touchEndX < touchStartX - 50) {
            avancarSlide();
        }
        if (touchEndX > touchStartX + 50) {
            voltarSlide();
        }
    }
}

// ===== VERIFICAR SE PRECISA FAZER ONBOARDING =====
function verificarOnboarding() {
    const path = window.location.pathname;
    
    const paginasExcluidas = [
        '/onboarding/',
        '/auth/',
        '/pro/'
    ];
    
    const isExcluida = paginasExcluidas.some(p => path.startsWith(p));
    
    if (!isExcluida && !UserData.isOnboardingComplete()) {
        window.location.href = '/onboarding/welcome/';
    }
}

if (!window.location.pathname.startsWith('/onboarding/')) {
    document.addEventListener('DOMContentLoaded', verificarOnboarding);
}