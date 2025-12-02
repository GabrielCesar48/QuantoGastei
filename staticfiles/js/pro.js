// ===== PÁGINA PRO - COMPRAS E RESTAURAÇÃO =====

async function verificarStatusPRO() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    
    if (userData.isPRO && userData.proExpiresAt) {
        const expira = new Date(userData.proExpiresAt);
        if (expira > new Date()) {
            return true;
        }
    }
    
    return false;
}

async function comprarPRO(plano) {
    console.log('Iniciando compra PRO:', plano);
    
    const produtos = {
        'mensal': 'com.quantogastei.pro.mensal',
        'anual': 'com.quantogastei.pro.anual'
    };
    
    const productId = produtos[plano];
    
    try {
        // TODO: Em produção, integrar Google Play Billing:
        // const purchase = await GooglePlayBilling.launchBillingFlow(productId);
        
        const purchaseToken = 'fake_token_' + Date.now();
        
        const response = await fetch('/api/payment/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                purchase_token: purchaseToken,
                product_id: productId,
                plano: plano
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            userData.isPRO = true;
            userData.proExpiresAt = data.expires_at;
            userData.proPlan = plano;
            localStorage.setItem('userData', JSON.stringify(userData));
            
            alert('🎉 Parabéns! Você agora é PRO!');
            window.location.href = '/home/';
        } else {
            throw new Error('Falha na validação da compra');
        }
        
    } catch (error) {
        console.error('Erro ao comprar PRO:', error);
        alert('Erro ao processar compra. Tente novamente.');
    }
}

function restaurarLicenca() {
    document.getElementById('modalRestaurar').classList.add('show');
}

function fecharModalRestaurar() {
    document.getElementById('modalRestaurar').classList.remove('show');
}

async function loginGoogleRestaurar() {
    try {
        window.location.href = '/auth/google/?action=restore';
    } catch (error) {
        console.error('Erro ao fazer login com Google:', error);
        alert('Erro ao conectar com Google. Tente novamente.');
    }
}

function mostrarLicencaNaoEncontrada(email) {
    document.getElementById('emailUsuario').textContent = email;
    document.getElementById('modalNaoEncontrada').classList.add('show');
}

function fecharModalNaoEncontrada() {
    document.getElementById('modalNaoEncontrada').classList.remove('show');
}

function comprarNovamente() {
    fecharModalNaoEncontrada();
    document.querySelector('.pricing-section').scrollIntoView({
        behavior: 'smooth'
    });
}

// Callback do Google OAuth
const urlParams = new URLSearchParams(window.location.search);
const googleToken = urlParams.get('token');
const action = urlParams.get('action');
const email = urlParams.get('email');

if (googleToken && action === 'restore') {
    (async function() {
        try {
            const response = await fetch('/api/payment/status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    google_token: googleToken,
                    email: email
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.has_active_subscription) {
                    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
                    userData.isPRO = true;
                    userData.proExpiresAt = data.expires_at;
                    userData.proPlan = data.plan;
                    userData.googleEmail = email;
                    localStorage.setItem('userData', JSON.stringify(userData));
                    
                    alert('✅ Licença restaurada com sucesso!');
                    window.location.href = '/home/';
                } else {
                    mostrarLicencaNaoEncontrada(email);
                }
            } else {
                throw new Error('Erro ao verificar assinatura');
            }
            
        } catch (error) {
            console.error('Erro ao restaurar licença:', error);
            alert('Erro ao verificar assinatura. Tente novamente.');
        }
    })();
}

window.onclick = function(event) {
    const modalRestaurar = document.getElementById('modalRestaurar');
    const modalNaoEncontrada = document.getElementById('modalNaoEncontrada');
    
    if (event.target === modalRestaurar) {
        fecharModalRestaurar();
    }
    if (event.target === modalNaoEncontrada) {
        fecharModalNaoEncontrada();
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    const isPRO = await verificarStatusPRO();
    
    if (isPRO) {
        const header = document.querySelector('.pro-header-content');
        if (header) {
            header.innerHTML += `
                <div class="alert alert-success" style="margin-top: 20px;">
                    ✅ Você já é PRO! Aproveite todos os recursos.
                </div>
            `;
        }
    }
});