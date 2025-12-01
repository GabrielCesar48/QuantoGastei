// ===== HELPER PARA CHAMADAS À API =====

const API_BASE_URL = '/api';

// Gerenciamento de Token
const TokenManager = {
    setTokens(access, refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    },
    
    getAccessToken() {
        return localStorage.getItem('access_token');
    },
    
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    
    isAuthenticated() {
        return !!this.getAccessToken();
    }
};

// Helper para fazer requisições autenticadas
async function fetchAPI(url, options = {}) {
    const token = TokenManager.getAccessToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(API_BASE_URL + url, config);
        
        // Token expirado? Tentar renovar
        if (response.status === 401 && token) {
            const renewed = await renewToken();
            if (renewed) {
                // Tentar novamente com novo token
                headers['Authorization'] = `Bearer ${TokenManager.getAccessToken()}`;
                return await fetch(API_BASE_URL + url, { ...options, headers });
            } else {
                // Renovação falhou, redirecionar para login
                TokenManager.clearTokens();
                window.location.href = '/';
                return null;
            }
        }
        
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Renovar token
async function renewToken() {
    const refreshToken = TokenManager.getRefreshToken();
    
    if (!refreshToken) return false;
    
    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            TokenManager.setTokens(data.access, refreshToken);
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Erro ao renovar token:', error);
        return false;
    }
}

// API de Autenticação
const AuthAPI = {
    async login(username, password) {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            TokenManager.setTokens(data.access, data.refresh);
            return { success: true, data };
        }
        
        const error = await response.json();
        return { success: false, error };
    },
    
    async registro(userData) {
        const response = await fetch(API_BASE_URL + '/usuarios/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const data = await response.json();
            return { success: true, data };
        }
        
        const error = await response.json();
        return { success: false, error };
    },
    
    logout() {
        TokenManager.clearTokens();
        window.location.href = '/';
    },
    
    async getMe() {
        const response = await fetchAPI('/usuarios/me/');
        if (response && response.ok) {
            return await response.json();
        }
        return null;
    }
};

// API de Contas
const ContasAPI = {
    async listar() {
        const response = await fetchAPI('/contas/');
        if (response && response.ok) {
            return await response.json();
        }
        return [];
    },
    
    async criar(contaData) {
        const response = await fetchAPI('/contas/', {
            method: 'POST',
            body: JSON.stringify(contaData)
        });
        
        if (response && response.ok) {
            return { success: true, data: await response.json() };
        }
        
        const error = response ? await response.json() : {};
        return { success: false, error };
    },
    
    async atualizar(id, contaData) {
        const response = await fetchAPI(`/contas/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(contaData)
        });
        
        if (response && response.ok) {
            return { success: true, data: await response.json() };
        }
        
        const error = response ? await response.json() : {};
        return { success: false, error };
    },
    
    async deletar(id) {
        const response = await fetchAPI(`/contas/${id}/`, {
            method: 'DELETE'
        });
        
        return response && response.ok;
    }
};

// API de Categorias
const CategoriasAPI = {
    async listar() {
        const response = await fetchAPI('/categorias/');
        if (response && response.ok) {
            return await response.json();
        }
        return [];
    },
    
    async criar(categoriaData) {
        const response = await fetchAPI('/categorias/', {
            method: 'POST',
            body: JSON.stringify(categoriaData)
        });
        
        if (response && response.ok) {
            return { success: true, data: await response.json() };
        }
        
        const error = response ? await response.json() : {};
        return { success: false, error };
    }
};

// API de Transações
const TransacoesAPI = {
    async listar(filtros = {}) {
        let url = '/transacoes/?';
        
        Object.keys(filtros).forEach(key => {
            if (filtros[key]) {
                url += `${key}=${filtros[key]}&`;
            }
        });
        
        const response = await fetchAPI(url);
        if (response && response.ok) {
            return await response.json();
        }
        return [];
    },
    
    async criar(transacaoData) {
        const response = await fetchAPI('/transacoes/', {
            method: 'POST',
            body: JSON.stringify(transacaoData)
        });
        
        if (response && response.ok) {
            return { success: true, data: await response.json() };
        }
        
        const error = response ? await response.json() : {};
        return { success: false, error };
    },
    
    async deletar(id) {
        const response = await fetchAPI(`/transacoes/${id}/`, {
            method: 'DELETE'
        });
        
        return response && response.ok;
    },
    
    async resumoMensal(mes, ano) {
        const response = await fetchAPI(`/transacoes/resumo_mensal/?mes=${mes}&ano=${ano}`);
        if (response && response.ok) {
            return await response.json();
        }
        return null;
    }
};

// Helpers de formatação
const Formatters = {
    moeda(valor) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    },
    
    data(dataString) {
        const data = new Date(dataString + 'T00:00:00');
        return data.toLocaleDateString('pt-BR');
    },
    
    dataInput(dataString) {
        // Converte "DD/MM/YYYY" para "YYYY-MM-DD"
        if (!dataString) {
            const hoje = new Date();
            const ano = hoje.getFullYear();
            const mes = String(hoje.getMonth() + 1).padStart(2, '0');
            const dia = String(hoje.getDate()).padStart(2, '0');
            return `${ano}-${mes}-${dia}`;
        }
        return dataString;
    }
};