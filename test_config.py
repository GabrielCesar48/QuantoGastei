# SCRIPT DE TESTE - Salve como test_config.py na raiz do projeto

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings

print("=" * 60)
print("🔍 TESTE DE CONFIGURAÇÃO GOOGLE OAUTH")
print("=" * 60)
print()

# Testar variáveis
print("📁 Arquivo .env:")
env_path = BASE_DIR / '.env'
if env_path.exists():
    print(f"   ✅ Existe: {env_path}")
    print()
    print("📄 Conteúdo do .env:")
    with open(env_path, 'r') as f:
        for line in f:
            if 'GOOGLE' in line:
                # Censurar valores
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    censored = value[:20] + '...' if len(value) > 20 else value
                    print(f"   {key}={censored}")
else:
    print(f"   ❌ NÃO EXISTE: {env_path}")

print()
print("⚙️  Configurações do Django:")
print(f"   GOOGLE_CLIENT_ID: {getattr(settings, 'GOOGLE_CLIENT_ID', 'NÃO DEFINIDO')[:30]}...")
print(f"   GOOGLE_CLIENT_SECRET: {getattr(settings, 'GOOGLE_CLIENT_SECRET', 'NÃO DEFINIDO')[:30]}...")

print()
print("=" * 60)

# Verificar se está vazio
client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

if not client_id:
    print("❌ ERRO: GOOGLE_CLIENT_ID está VAZIO!")
    print()
    print("💡 SOLUÇÃO:")
    print("   1. Verifique se o arquivo .env está na raiz do projeto")
    print("   2. Verifique se tem a linha: GOOGLE_CLIENT_ID=seu-id-aqui")
    print("   3. Não pode ter espaços: GOOGLE_CLIENT_ID = xxx (ERRADO)")
    print("   4. Deve ser: GOOGLE_CLIENT_ID=xxx (CERTO)")
    print("   5. Reinicie o servidor após salvar o .env")
else:
    print("✅ GOOGLE_CLIENT_ID configurado corretamente!")

print()

if not client_secret:
    print("❌ ERRO: GOOGLE_CLIENT_SECRET está VAZIO!")
else:
    print("✅ GOOGLE_CLIENT_SECRET configurado corretamente!")

print()
print("=" * 60)