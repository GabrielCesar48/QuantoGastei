// ===== ONBOARDING - SISTEMA DE BOAS-VINDAS =====

// Função para ler cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// ===== PROCESSAR COOKIES IMEDIATAMENTE =====
(function processarCookies() {
    console.log('[ONBOARDING] 🔍 Verificando cookies...');
    
    const jwtAccessCookie = getCookie('jwt_access');
    const jwtRefreshCookie = getCookie('jwt_refresh');
    const onboardingCompleteCookie = getCookie('onboardingComplete');
    
    console.log('[ONBOARDING] Cookies encontrados:');
    console.log('  - jwt_access:', jwtAccessCookie ? 'SIM' : 'NÃO');
    console.log('  - jwt_refresh:', jwtRefreshCookie ? 'SIM' : 'NÃO');
    console.log('  - onboardingComplete:', onboardingCompleteCookie ? onboardingCompleteCookie : 'NÃO');
    
    if (jwtAccessCookie && jwtRefreshCookie) {
        console.log('[ONBOARDING] ✅ Salvando tokens no localStorage...');
        localStorage.setItem('access_token', jwtAccessCookie);
        localStorage.setItem('refresh_token', jwtRefreshCookie);
        
        // Limpar cookies
        document.cookie = 'jwt_access=; Max-Age=0; path=/';
        document.cookie = 'jwt_refresh=; Max-Age=0; path=/';
        console.log('[ONBOARDING] 🧹 Cookies JWT limpos');
    }
    
    // Se tem cookie de onboarding completo, salvar no localStorage
    if (onboardingCompleteCookie === 'true') {
        console.log('[ONBOARDING] ✅ Marcando onboarding como completo no localStorage...');
        localStorage.setItem('onboardingComplete', 'true');
        // Limpar cookie
        document.cookie = 'onboardingComplete=; Max-Age=0; path=/';
        
        console.log('[ONBOARDING] ✅ Onboarding marcado como completo via cookie');
    } else {
        console.log('[ONBOARDING] ⚠️  Cookie onboardingComplete não encontrado ou não é "true"');
    }
})();

// Aplicar dark mode imediatamente
const darkMode = localStorage.getItem('darkMode') === 'true';
if (darkMode) {
    document.body.classList.add('dark-mode');
}

// ===== DADOS TEMPORÁRIOS (SESSION STORAGE) =====
const TempData = {
    save(data) {
        const current = this.get() || {};
        const updated = { ...current, ...data };
        sessionStorage.setItem('onboardingData', JSON.stringify(updated));
    },
    
    get() {
        const data = sessionStorage.getItem('onboardingData');
        return data ? JSON.parse(data) : null;
    },
    
    clear() {
        sessionStorage.removeItem('onboardingData');
    }
};

// Verificar se onboarding está completo
function isOnboardingComplete() {
    return localStorage.getItem('onboardingComplete') === 'true';
}

function setOnboardingComplete() {
    localStorage.setItem('onboardingComplete', 'true');
}

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
    
    // Salvar temporariamente
    TempData.save({
        first_name: nome.value.trim()
    });
    
    window.location.href = '/onboarding/step2/';
}

function loginComGoogle() {
    // Marcar que veio do Google para ir direto para step2
    sessionStorage.setItem('fromGoogle', 'true');
    window.location.href = '/auth/google/?action=onboarding';
}

// ===== STEP 2 (TELEFONE E PREFERÊNCIAS) =====
if (document.getElementById('telefone')) {
    const telefoneInput = document.getElementById('telefone');
    const darkModeToggle = document.getElementById('darkMode');
    const notificacoesToggle = document.getElementById('notificacoes');
    const nomeInput = document.getElementById('nome');
    const emailInput = document.getElementById('email');
    
    // Carregar dados temporários ou do Google
    const tempData = TempData.get();
    if (tempData) {
        if (tempData.first_name) {
            nomeInput.value = tempData.first_name;
        }
        if (tempData.email) {
            emailInput.value = tempData.email;
        }
    }
    
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
    
    // Carregar dark mode salvo
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    darkModeToggle.checked = savedDarkMode;
    
    window.voltarPasso = function() {
        window.location.href = '/onboarding/welcome/';
    };
    
    // Submeter formulário
    const formOnboarding = document.getElementById('formOnboarding');
    if (formOnboarding) {
        formOnboarding.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const btnSalvar = document.getElementById('btnSalvar');
            const telefone = telefoneInput.value.replace(/\D/g, '');
            const darkMode = darkModeToggle.checked;
            const notificacoes = notificacoesToggle.checked;
            const nome = nomeInput.value.trim();
            const email = emailInput.value.trim();
            
            // Validar telefone
            if (!telefone || telefone.length < 10) {
                showAlert('Por favor, digite um telefone válido', 'danger');
                telefoneInput.focus();
                return;
            }
            
            // Desabilitar botão
            btnSalvar.disabled = true;
            btnSalvar.innerHTML = '<span class="loading"></span>';
            
            try {
                // Verificar se já tem token (veio do Google)
                const token = TokenManager.getAccessToken();
                
                if (token) {
                    // Atualizar preferências do usuário existente
                    const response = await fetch('/api/usuarios/update_preferences/', {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            telefone: telefone,
                            dark_mode: darkMode,
                            notificacoes_ativas: notificacoes
                        })
                    });
                    
                    if (response.ok) {
                        // Salvar preferências locais
                        localStorage.setItem('darkMode', darkMode);
                        
                        // Limpar dados temporários
                        TempData.clear();
                        setOnboardingComplete();
                        
                        // Ir para tutorial
                        window.location.href = '/onboarding/tutorial/';
                    } else {
                        throw new Error('Erro ao salvar preferências');
                    }
                } else {
                    // Criar novo usuário (não veio do Google)
                    // Gerar username e senha aleatória
                    const username = email.split('@')[0] + Math.floor(Math.random() * 1000);
                    const senha = Math.random().toString(36).slice(-8);
                    
                    const response = await fetch('/api/usuarios/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            email: email,
                            first_name: nome,
                            password: senha,
                            password_confirm: senha,
                            telefone: telefone
                        })
                    });
                    
                    if (response.ok) {
                        // Fazer login automático
                        const loginResponse = await fetch('/api/token/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                username: username,
                                password: senha
                            })
                        });
                        
                        if (loginResponse.ok) {
                            const tokens = await loginResponse.json();
                            TokenManager.setTokens(tokens.access, tokens.refresh);
                            
                            // Atualizar preferências
                            await fetch('/api/usuarios/update_preferences/', {
                                method: 'PATCH',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${tokens.access}`
                                },
                                body: JSON.stringify({
                                    dark_mode: darkMode,
                                    notificacoes_ativas: notificacoes
                                })
                            });
                            
                            // Salvar preferências locais
                            localStorage.setItem('darkMode', darkMode);
                            
                            // Limpar dados temporários
                            TempData.clear();
                            setOnboardingComplete();
                            
                            // Ir para tutorial
                            window.location.href = '/onboarding/tutorial/';
                        } else {
                            throw new Error('Erro ao fazer login');
                        }
                    } else {
                        const error = await response.json();
                        throw new Error(error.detail || 'Erro ao criar conta');
                    }
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert(error.message || 'Erro ao salvar dados. Tente novamente.', 'danger');
                btnSalvar.disabled = false;
                btnSalvar.innerHTML = `
                    Próximo
                    <span class="material-symbols-outlined">arrow_forward</span>
                `;
            }
        });
    }
}

// Helper para mostrar alertas
function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
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
            // Marcar onboarding como completo e ir para home
            setOnboardingComplete();
            window.location.href = '/home/';
        }
    };
    
    // Swipe support
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
    
    console.log('[ONBOARDING] 🔍 Verificando se precisa onboarding...');
    console.log('  - Página atual:', path);
    console.log('  - localStorage.onboardingComplete:', localStorage.getItem('onboardingComplete'));
    
    const paginasExcluidas = [
        '/onboarding/',
        '/auth/',
        '/pro/',
        '/',
        '/login/',
        '/registro/'
    ];
    
    const isExcluida = paginasExcluidas.some(p => path === p || path.startsWith(p));
    
    console.log('  - Página excluída?', isExcluida);
    console.log('  - Onboarding completo?', isOnboardingComplete());
    
    // Se não está em página excluída e não completou onboarding
    if (!isExcluida && !isOnboardingComplete()) {
        console.log('[ONBOARDING] ❌ Onboarding não completo - redirecionando para /onboarding/welcome/');
        window.location.href = '/onboarding/welcome/';
    } else {
        console.log('[ONBOARDING] ✅ Onboarding OK ou página excluída - não redirecionar');
    }
}

// Verificar onboarding ao carregar página (exceto nas páginas de onboarding)
if (!window.location.pathname.startsWith('/onboarding/') && 
    !window.location.pathname.startsWith('/auth/')) {
    document.addEventListener('DOMContentLoaded', verificarOnboarding);
}