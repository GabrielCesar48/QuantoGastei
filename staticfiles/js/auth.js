// ===== AUTENTICAÇÃO =====

// Verificar se já está logado
if (TokenManager.isAuthenticated() && window.location.pathname === '/') {
    window.location.href = '/home/';
}

// Helpers de UI
function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alert-container');
    alertContainer.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (loading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span>';
    } else {
        btn.disabled = false;
        btn.innerHTML = btnId === 'btnLogin' ? 'Entrar' : 'Criar Conta';
    }
}

// Login
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        setLoading('btnLogin', true);
        
        const result = await AuthAPI.login(username, password);
        
        if (result.success) {
            showAlert('Login realizado com sucesso!', 'success');
            setTimeout(() => {
                window.location.href = '/home/';
            }, 1000);
        } else {
            setLoading('btnLogin', false);
            const errorMsg = result.error.detail || 'Usuário ou senha incorretos';
            showAlert(errorMsg, 'danger');
        }
    });
}

// Registro
const registroForm = document.getElementById('registroForm');
if (registroForm) {
    registroForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const first_name = document.getElementById('first_name').value;
        const password = document.getElementById('password').value;
        const password_confirm = document.getElementById('password_confirm').value;
        
        // Validar senhas
        if (password !== password_confirm) {
            showAlert('As senhas não conferem', 'danger');
            return;
        }
        
        if (password.length < 8) {
            showAlert('A senha deve ter pelo menos 8 caracteres', 'danger');
            return;
        }
        
        setLoading('btnRegistro', true);
        
        const result = await AuthAPI.registro({
            username,
            email,
            first_name,
            password,
            password_confirm
        });
        
        if (result.success) {
            showAlert('Conta criada com sucesso! Redirecionando...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            setLoading('btnRegistro', false);
            
            // Formatar erros
            let errorMsg = 'Erro ao criar conta. ';
            if (result.error.username) {
                errorMsg += 'Nome de usuário já existe. ';
            }
            if (result.error.email) {
                errorMsg += 'E-mail já cadastrado. ';
            }
            if (result.error.password) {
                errorMsg += result.error.password[0];
            }
            
            showAlert(errorMsg, 'danger');
        }
    });
}