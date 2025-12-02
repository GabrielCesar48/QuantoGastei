// ===== DASHBOARD =====

// Verificar autenticação
if (!TokenManager.isAuthenticated()) {
    window.location.href = '/';
}

// Estado Global
let state = {
    usuario: null,
    contas: [],
    contaSelecionada: null,
    categorias: [],
    transacoes: [],
    resumoMensal: null,
    mesAtual: new Date().getMonth() + 1,
    anoAtual: new Date().getFullYear()
};

// Chart.js instance
let chartCategoria = null;

// ===== INICIALIZAÇÃO =====
async function init() {
    await carregarUsuario();
    await carregarContas();
    await carregarCategorias();
    await carregarResumoMensal();
    await carregarUltimasTransacoes();
}

// ===== CARREGAR DADOS =====
async function carregarUsuario() {
    const usuario = await AuthAPI.getMe();
    if (usuario) {
        state.usuario = usuario;
        const userName = document.getElementById('user-name');
        if (userName) {
            userName.textContent = usuario.first_name || usuario.username;
        }
    }
}

async function carregarContas() {
    const response = await ContasAPI.listar();
    
    // A API pode retornar um objeto paginado ou array direto
    state.contas = Array.isArray(response) ? response : (response.results || []);
    
    // Adicionar opção "Todas as contas"
    state.contaSelecionada = null;
    
    renderizarContas();
}

async function carregarCategorias() {
    const response = await CategoriasAPI.listar();
    state.categorias = Array.isArray(response) ? response : (response.results || []);
}

async function carregarResumoMensal() {
    const resumo = await TransacoesAPI.resumoMensal(state.mesAtual, state.anoAtual);
    state.resumoMensal = resumo;
    
    renderizarResumoMensal();
    renderizarGrafico();
}

async function carregarUltimasTransacoes() {
    const response = await TransacoesAPI.listar({
        ordering: '-data,-created_at'
    });
    
    state.transacoes = Array.isArray(response) ? response : (response.results || []);
    renderizarUltimasTransacoes();
}

// ===== RENDERIZAÇÃO =====
function renderizarContas() {
    const container = document.getElementById('contasSelector');
    if (!container) return;
    
    // Verificar se contas é array
    if (!Array.isArray(state.contas)) {
        state.contas = [];
    }
    
    let html = `
        <div class="conta-card ${!state.contaSelecionada ? 'active' : ''}" onclick="selecionarConta(null)">
            <div class="conta-icone">
                <span class="material-symbols-outlined">account_balance_wallet</span>
            </div>
            <div class="conta-nome">Todas</div>
            <div class="conta-saldo">${calcularSaldoTotal()}</div>
        </div>
    `;
    
    state.contas.forEach(conta => {
        const ativo = state.contaSelecionada?.id === conta.id;
        html += `
            <div class="conta-card ${ativo ? 'active' : ''}" onclick="selecionarConta(${conta.id})">
                <div class="conta-icone" style="color: ${conta.cor}">
                    <span class="material-symbols-outlined">${conta.icone}</span>
                </div>
                <div class="conta-nome">${conta.nome}</div>
                <div class="conta-saldo">${Formatters.moeda(conta.saldo_atual)}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function calcularSaldoTotal() {
    if (!Array.isArray(state.contas) || state.contas.length === 0) {
        return Formatters.moeda(0);
    }
    
    const total = state.contas.reduce((acc, conta) => acc + parseFloat(conta.saldo_atual), 0);
    return Formatters.moeda(total);
}

function selecionarConta(contaId) {
    state.contaSelecionada = contaId ? state.contas.find(c => c.id === contaId) : null;
    renderizarContas();
    carregarUltimasTransacoes();
}

function renderizarResumoMensal() {
    if (!state.resumoMensal) return;
    
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    
    document.getElementById('resumoMes').textContent = 
        `${meses[state.mesAtual - 1]} ${state.anoAtual}`;
    
    document.getElementById('totalReceitas').textContent = 
        Formatters.moeda(state.resumoMensal.receitas);
    
    document.getElementById('totalDespesas').textContent = 
        Formatters.moeda(state.resumoMensal.despesas);
    
    document.getElementById('saldoMes').textContent = 
        Formatters.moeda(state.resumoMensal.saldo);
}

function renderizarGrafico() {
    if (!state.resumoMensal || !state.resumoMensal.gastos_por_categoria) return;
    
    const ctx = document.getElementById('chartCategoria');
    if (!ctx) return;
    
    const dados = state.resumoMensal.gastos_por_categoria;
    
    if (dados.length === 0) {
        ctx.parentElement.innerHTML = '<p style="text-align: center; color: #666;">Nenhum gasto registrado neste mês</p>';
        return;
    }
    
    // Destruir chart anterior
    if (chartCategoria) {
        chartCategoria.destroy();
    }
    
    const labels = dados.map(d => d.categoria__nome);
    const values = dados.map(d => parseFloat(d.total));
    const cores = dados.map(d => d.categoria__cor);
    
    chartCategoria = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: cores,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = Formatters.moeda(context.parsed);
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percent = ((context.parsed / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderizarUltimasTransacoes() {
    const container = document.getElementById('ultimasTransacoes');
    if (!container) return;
    
    let transacoesFiltradas = state.transacoes;
    
    if (state.contaSelecionada) {
        transacoesFiltradas = state.transacoes.filter(t => 
            t.conta_origem === state.contaSelecionada.id || 
            t.conta_destino === state.contaSelecionada.id
        );
    }
    
    if (transacoesFiltradas.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Nenhuma transação registrada</p>';
        return;
    }
    
    // Mostrar últimas 10
    const ultimas = transacoesFiltradas.slice(0, 10);
    
    let html = '';
    ultimas.forEach(transacao => {
        const icone = transacao.categoria_icone || 'more_horiz';
        const sinal = transacao.tipo === 'receita' ? '+' : '-';
        const classe = transacao.tipo === 'receita' ? 'receita' : 'despesa';
        
        html += `
            <div class="transacao-item">
                <div class="transacao-icone">
                    <span class="material-symbols-outlined">${icone}</span>
                </div>
                <div class="transacao-info">
                    <div class="transacao-descricao">${transacao.descricao}</div>
                    <div class="transacao-categoria">
                        ${transacao.categoria_nome || 'Sem categoria'} • ${Formatters.data(transacao.data)}
                    </div>
                </div>
                <div class="transacao-valor ${classe}">
                    ${sinal} ${Formatters.moeda(Math.abs(transacao.valor))}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// ===== MODAL DE TRANSAÇÃO =====
function abrirModal(tipo) {
    const modal = document.getElementById('modalTransacao');
    const titulo = document.getElementById('modalTitle');
    const tipoInput = document.getElementById('tipoTransacao');
    const grupoContaDestino = document.getElementById('grupoContaDestino');
    const grupoCategoria = document.getElementById('grupoCategoria');
    
    // Configurar título e tipo
    const titulos = {
        'receita': 'Nova Receita',
        'despesa': 'Nova Despesa',
        'transferencia': 'Nova Transferência'
    };
    
    titulo.textContent = titulos[tipo];
    tipoInput.value = tipo;
    
    // Mostrar/ocultar campos
    if (tipo === 'transferencia') {
        grupoContaDestino.style.display = 'block';
        grupoCategoria.style.display = 'none';
    } else {
        grupoContaDestino.style.display = 'none';
        grupoCategoria.style.display = 'block';
    }
    
    // Preencher selects
    preencherSelectContas();
    preencherSelectCategorias(tipo);
    
    // Definir data de hoje
    document.getElementById('data').value = Formatters.dataInput();
    
    modal.classList.add('show');
}

function fecharModal() {
    const modal = document.getElementById('modalTransacao');
    modal.classList.remove('show');
    document.getElementById('formTransacao').reset();
}

function preencherSelectContas() {
    const selectOrigem = document.getElementById('conta_origem');
    const selectDestino = document.getElementById('conta_destino');
    
    // Verificar se contas é array
    if (!Array.isArray(state.contas)) {
        state.contas = [];
    }
    
    let options = '<option value="">Selecione...</option>';
    state.contas.forEach(conta => {
        options += `<option value="${conta.id}">${conta.nome}</option>`;
    });
    
    selectOrigem.innerHTML = options;
    selectDestino.innerHTML = options;
}

function preencherSelectCategorias(tipo) {
    const select = document.getElementById('categoria');
    
    // Verificar se categorias é array
    if (!Array.isArray(state.categorias)) {
        state.categorias = [];
    }
    
    const categoriasFiltradas = state.categorias.filter(c => c.tipo === tipo);
    
    let options = '<option value="">Selecione...</option>';
    categoriasFiltradas.forEach(cat => {
        options += `<option value="${cat.id}">${cat.nome}</option>`;
    });
    
    select.innerHTML = options;
}

// Submit do formulário de transação
const formTransacao = document.getElementById('formTransacao');
if (formTransacao) {
    formTransacao.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const tipo = document.getElementById('tipoTransacao').value;
        const descricao = document.getElementById('descricao').value;
        const valor = parseFloat(document.getElementById('valor').value);
        const data = document.getElementById('data').value;
        const conta_origem = parseInt(document.getElementById('conta_origem').value);
        const observacoes = document.getElementById('observacoes').value;
        
        const transacaoData = {
            tipo,
            descricao,
            valor,
            data,
            conta_origem,
            observacoes
        };
        
        // Campos opcionais
        if (tipo === 'transferencia') {
            const conta_destino = parseInt(document.getElementById('conta_destino').value);
            if (conta_destino) {
                transacaoData.conta_destino = conta_destino;
            }
        } else {
            const categoria = document.getElementById('categoria').value;
            if (categoria) {
                transacaoData.categoria = parseInt(categoria);
            }
        }
        
        const result = await TransacoesAPI.criar(transacaoData);
        
        if (result.success) {
            fecharModal();
            // Recarregar dados
            await carregarContas();
            await carregarResumoMensal();
            await carregarUltimasTransacoes();
        } else {
            alert('Erro ao criar transação: ' + JSON.stringify(result.error));
        }
    });
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('modalTransacao');
    if (event.target === modal) {
        fecharModal();
    }
}

// Logout
function logout() {
    if (confirm('Deseja realmente sair?')) {
        AuthAPI.logout();
    }
}

// Inicializar ao carregar página
document.addEventListener('DOMContentLoaded', init);

async function carregarUltimasTransacoes() {
    // Esconder skeleton
    const skeleton = document.querySelector('.skeleton-container');
    if (skeleton) skeleton.style.display = 'none';
    
    const response = await TransacoesAPI.listar({
        ordering: '-data,-created_at'
    });
    
    state.transacoes = Array.isArray(response) ? response : (response.results || []);
    renderizarUltimasTransacoes();
}