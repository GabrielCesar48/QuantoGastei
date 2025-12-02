from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import (
    UsuarioViewSet,
    login_view,
    registro_view,
    home_view,
    contas_view,
    transacoes_view,
    configuracoes_view,
)
from core.oauth_views import (
    onboarding_welcome,
    onboarding_step2,
    onboarding_tutorial,
    pro_page,
    google_oauth_redirect,
    google_oauth_callback,
    verify_purchase,
    check_subscription_status,
    google_play_webhook,
)
from contas.views import ContaViewSet
from transacoes.views import CategoriaViewSet, TransacaoViewSet

# Router da API
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'transacoes', TransacaoViewSet, basename='transacao')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ===== ONBOARDING (NOVO) =====
    path('', onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/welcome/', onboarding_welcome, name='onboarding_welcome_alt'),
    path('onboarding/step2/', onboarding_step2, name='onboarding_step2'),
    path('onboarding/tutorial/', onboarding_tutorial, name='onboarding_tutorial'),
    
    # ===== GOOGLE OAUTH (NOVO) =====
    path('auth/google/', google_oauth_redirect, name='google_oauth'),
    path('auth/google/callback/', google_oauth_callback, name='google_oauth_callback'),
    
    # ===== PÁGINAS PRINCIPAIS =====
    path('home/', home_view, name='home'),
    path('contas/', contas_view, name='contas'),
    path('transacoes/', transacoes_view, name='transacoes'),
    path('configuracoes/', configuracoes_view, name='configuracoes'),
    path('pro/', pro_page, name='pro'),
    
    # ===== AUTH LEGACY (manter para compatibilidade) =====
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    
    # ===== API REST =====
    path('api/', include(router.urls)),
    
    # ===== API DE PAGAMENTOS (NOVO) =====
    path('api/payment/verify/', verify_purchase, name='verify_purchase'),
    path('api/payment/status/', check_subscription_status, name='subscription_status'),
    path('api/payment/hooks/', google_play_webhook, name='google_play_webhook'),
    
    # ===== JWT AUTH =====
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)