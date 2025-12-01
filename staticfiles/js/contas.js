// ===== GERENCIAR CONTAS =====

if (!TokenManager.isAuthenticated()) {
    window.location.href = '/';
}

let contas = [];

async function carregarContas() {
    contas = await ContasAPI.listar();
    renderizarContas();
}

function renderizarContas() {
    const container = document.getElementById('listaContas');
    
    if (contas.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Nenhuma conta cadastrada</p>';
        return;
    }
    
    let html = '';
    contas.forEach(conta => {
        html += `
            <div class="transacao-item" style="margin-bottom: 15px;">
                <div class="transacao-icone" style="background-color: ${conta.cor}20;">
                    <span class="material-symbols-outlined" style="color: ${conta.cor};">${conta.icone}</span>
                </div>
                <div class="transacao-info">
                    <div class="transacao-descricao">${conta.nome}</div>
                    <div class="transacao-categoria">${conta.tipo.replace('_', ' ')}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: 600; color: #12A454;">
                        ${Formatters.moeda(conta.saldo_atual)}
                    </div>
                    <div style="margin-top: 5px;">
                        <button onclick="editarConta(${conta.id})" style="background: none; border: none; cursor: pointer; color: #3B82F6; margin-right: 10px;">
                            <span class="material-symbols-outlined">edit</span>
                        </button>
                        <button onclick="deletarConta(${conta.id})" style="background: none; border: none; cursor: pointer; color: #E83F5B;">
                            <span class="material-symbols-outlined">delete</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function abrirModalConta() {
    document.getElementById('modalContaTitle').textContent = 'Nova Conta';
    document.getElementById('formConta').reset();
    document.getElementById('contaId').value = '';
    document.getElementById('modalConta').classList.add('show');
}

function fecharModalConta() {
    document.getElementById('modalConta').classList.remove('show');
}

function editarConta(id) {
    const conta = contas.find(c => c.id === id);
    if (!conta) return;
    
    document.getElementById('modalContaTitle').textContent = 'Editar Conta';
    document.getElementById('contaId').value = conta.id;
    document.getElementById('nome').value = conta.nome;
    document.getElementById('tipo').value = conta.tipo;
    document.getElementById('saldo_inicial').value = conta.saldo_inicial;
    document.getElementById('icone').value = conta.icone;
    document.getElementById('cor').value = conta.cor;
    
    document.getElementById('modalConta').classList.add('show');
}

async function deletarConta(id) {
    if (!confirm('Deseja realmente deletar esta conta? Todas as transações serão mantidas.')) {
        return;
    }
    
    const success = await ContasAPI.deletar(id);
    if (success) {
        await carregarContas();
    } else {
        alert('Erro ao deletar conta. Pode haver transações vinculadas.');
    }
}

// Submit do formulário
document.getElementById('formConta').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const contaId = document.getElementById('contaId').value;
    const contaData = {
        nome: document.getElementById('nome').value,
        tipo: document.getElementById('tipo').value,
        saldo_inicial: parseFloat(document.getElementById('saldo_inicial').value),
        icone: document.getElementById('icone').value,
        cor: document.getElementById('cor').value,
        ativa: true
    };
    
    let result;
    if (contaId) {
        result = await ContasAPI.atualizar(parseInt(contaId), contaData);
    } else {
        result = await ContasAPI.criar(contaData);
    }
    
    if (result.success) {
        fecharModalConta();
        await carregarContas();
    } else {
        alert('Erro ao salvar conta: ' + JSON.stringify(result.error));
    }
});

function logout() {
    if (confirm('Deseja realmente sair?')) {
        AuthAPI.logout();
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', carregarContas);