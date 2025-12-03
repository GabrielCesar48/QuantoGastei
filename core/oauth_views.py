from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests
from datetime import datetime, timedelta
from core.models import Usuario
from assinaturas.models import Assinatura, LogPagamento

# ===== ONBOARDING VIEWS =====

def onboarding_welcome(request):
    return render(request, 'onboarding/welcome.html')

def onboarding_step2(request):
    return render(request, 'onboarding/step2.html')

def onboarding_tutorial(request):
    return render(request, 'onboarding/tutorial.html')

def pro_page(request):
    return render(request, 'dashboard/pro.html')

# ===== GOOGLE OAUTH 2.0 =====

@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_redirect(request):
    action = request.GET.get('action', 'login')
    
    # CORRIGIDO: Verificar se existe e dar erro claro
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    
    # DEBUG: Verificar se está vazio
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
                <li>Se não funcionar, adicione direto no <code>settings.py</code>:<br>
                    <code>GOOGLE_CLIENT_ID = 'seu-id-aqui'</code>
                </li>
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
        
        else:
            usuario, created = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': name
                }
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