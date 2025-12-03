from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from datetime import datetime, timedelta
from core.models import Usuario
from assinaturas.models import Assinatura, LogPagamento

# ===== ONBOARDING VIEWS =====

def onboarding_welcome(request):
    return render(request, 'onboarding/welcome.html')

def onboarding_step2(request):
    # Passar dados do Google se existirem na session
    context = {
        'google_name': request.session.get('google_name', ''),
        'google_email': request.session.get('google_email', '')
    }
    
    # Limpar session após ler
    if 'google_name' in request.session:
        del request.session['google_name']
    if 'google_email' in request.session:
        del request.session['google_email']
    
    return render(request, 'onboarding/step2.html', context)

def onboarding_tutorial(request):
    return render(request, 'onboarding/tutorial.html')

def pro_page(request):
    return render(request, 'dashboard/pro.html')

# ===== GOOGLE OAUTH 2.0 =====

@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_redirect(request):
    action = request.GET.get('action', 'login')
    
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    
    # Verificar configuração
    if not client_id or not client_secret:
        return HttpResponse(f"""
            <h1>❌ Erro de Configuração OAuth</h1>
            <p><strong>GOOGLE_CLIENT_ID está vazio:</strong> {bool(client_id)}</p>
            <p><strong>GOOGLE_CLIENT_SECRET está vazio:</strong> {bool(client_secret)}</p>
            <hr>
            <h3>Como corrigir:</h3>
            <ol>
                <li>Verifique se o arquivo <code>.env</code> existe na raiz do projeto</li>
                <li>Verifique se tem as linhas:<br>
                    <code>GOOGLE_CLIENT_ID=seu-id-aqui<br>
                    GOOGLE_CLIENT_SECRET=seu-secret-aqui</code>
                </li>
                <li>Reinicie o servidor Django</li>
            </ol>
            <p><a href="/">← Voltar</a></p>
        """, status=500)
    
    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    
    scopes = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={' '.join(scopes)}&"
        f"access_type=offline&"
        f"state={action}"
    )
    
    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_callback(request):
    code = request.GET.get('code')
    action = request.GET.get('state', 'login')
    error = request.GET.get('error')
    
    if error:
        return redirect('/?error=google_auth_denied')
    
    if not code:
        return redirect('/?error=no_code')
    
    try:
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': request.build_absolute_uri('/auth/google/callback/'),
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        email = user_data.get('email')
        name = user_data.get('given_name', '')
        full_name = user_data.get('name', name)
        
        # DEBUG: Log para verificar fluxo
        print(f"[GOOGLE AUTH] Email: {email}, Action: {action}")
        
        # SEMPRE verificar se usuário existe primeiro
        usuario_existente = Usuario.objects.filter(email=email).first()
        
        # DEBUG: Verificar se encontrou usuário
        if usuario_existente:
            print(f"[GOOGLE AUTH] ✅ Usuário EXISTENTE encontrado: {usuario_existente.username} (ID: {usuario_existente.id})")
        else:
            print(f"[GOOGLE AUTH] ⚠️  Usuário NOVO - será criado")
        
        if action == 'restore':
            assinatura = Assinatura.objects.filter(
                usuario__email=email,
                status='ativa'
            ).first()
            
            if assinatura and assinatura.esta_ativa:
                redirect_url = (
                    f"/pro/?action=restore&token={access_token}&email={email}"
                    f"&has_pro=true&expires_at={assinatura.data_expiracao.isoformat()}"
                )
                return redirect(redirect_url)
            else:
                redirect_url = f"/pro/?action=restore&token={access_token}&email={email}&has_pro=false"
                return redirect(redirect_url)
        
        elif action == 'onboarding' or action == 'login':
            # SE USUÁRIO JÁ EXISTE - fazer login direto e ir para home
            if usuario_existente:
                print(f"[GOOGLE AUTH] 🔄 Fazendo login do usuário existente...")
                
                login(request, usuario_existente, backend='django.contrib.auth.backends.ModelBackend')
                
                print(f"[GOOGLE AUTH] ✅ Login feito com sucesso")
                
                # Gerar JWT tokens
                refresh = RefreshToken.for_user(usuario_existente)
                
                print(f"[GOOGLE AUTH] 🔑 JWT tokens gerados")
                
                # Salvar tokens nos cookies
                response = redirect('/home/')
                response.set_cookie('jwt_access', str(refresh.access_token), httponly=False, max_age=3600)
                response.set_cookie('jwt_refresh', str(refresh), httponly=False, max_age=604800)
                response.set_cookie('onboardingComplete', 'true', httponly=False, max_age=31536000)
                
                print(f"[GOOGLE AUTH] 🍪 Cookies configurados:")
                print(f"  - jwt_access: configurado")
                print(f"  - jwt_refresh: configurado")
                print(f"  - onboardingComplete: true")
                print(f"[GOOGLE AUTH] 🚀 Redirecionando para /home/")
                
                return response
            else:
                # USUÁRIO NOVO - criar e ir para step2
                usuario = Usuario.objects.create(
                    email=email,
                    username=email.split('@')[0] + str(Usuario.objects.count()),
                    first_name=name
                )
                
                # Fazer login
                login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                
                # Gerar JWT tokens
                refresh = RefreshToken.for_user(usuario)
                
                # Salvar dados na session para o JavaScript ler
                request.session['google_name'] = full_name
                request.session['google_email'] = email
                request.session['jwt_access'] = str(refresh.access_token)
                request.session['jwt_refresh'] = str(refresh)
                
                # Redirecionar para step2 (precisa completar telefone)
                return redirect('/onboarding/step2/')
        
        else:
            # Fallback: qualquer outro action ou sem action
            # Também verifica se usuário existe
            if usuario_existente:
                # Usuário existe - login direto
                login(request, usuario_existente, backend='django.contrib.auth.backends.ModelBackend')
                
                # Gerar JWT tokens
                refresh = RefreshToken.for_user(usuario_existente)
                
                # Salvar tokens nos cookies
                response = redirect('/home/')
                response.set_cookie('jwt_access', str(refresh.access_token), httponly=False, max_age=3600)
                response.set_cookie('jwt_refresh', str(refresh), httponly=False, max_age=604800)
                
                # IMPORTANTE: Marcar onboarding como completo
                response.set_cookie('onboardingComplete', 'true', httponly=False, max_age=31536000)
                
                print(f"[GOOGLE AUTH] ✅ Fallback - Login direto para home")
                
                return response
            else:
                # Usuário novo - criar
                usuario = Usuario.objects.create(
                    email=email,
                    username=email.split('@')[0] + str(Usuario.objects.count()),
                    first_name=name
                )
                
                login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
                
                return redirect('/home/')
    
    except Exception as e:
        print(f"Erro no OAuth callback: {e}")
        return redirect('/?error=oauth_failed')


# ===== API ENDPOINTS PARA PAGAMENTOS =====

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_purchase(request):
    purchase_token = request.data.get('purchase_token')
    product_id = request.data.get('product_id')
    plano = request.data.get('plano')
    
    if not all([purchase_token, product_id, plano]):
        return Response(
            {'error': 'Dados incompletos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # TODO: Validar com Google Play Developer API
        
        if plano == 'mensal':
            expira_em = datetime.now() + timedelta(days=30)
        else:
            expira_em = datetime.now() + timedelta(days=365)
        
        return Response({
            'success': True,
            'expires_at': expira_em.isoformat(),
            'plan': plano
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def check_subscription_status(request):
    google_token = request.data.get('google_token')
    email = request.data.get('email')
    
    if not all([google_token, email]):
        return Response(
            {'error': 'Dados incompletos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        usuario = Usuario.objects.filter(email=email).first()
        
        if not usuario:
            return Response({
                'has_active_subscription': False
            })
        
        assinatura = Assinatura.objects.filter(
            usuario=usuario,
            status='ativa'
        ).first()
        
        if assinatura and assinatura.esta_ativa:
            return Response({
                'has_active_subscription': True,
                'plan': assinatura.plano,
                'expires_at': assinatura.data_expiracao.isoformat()
            })
        else:
            return Response({
                'has_active_subscription': False
            })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def google_play_webhook(request):
    LogPagamento.objects.create(
        evento='webhook_recebido',
        payload=request.data
    )
    
    return Response({'received': True})