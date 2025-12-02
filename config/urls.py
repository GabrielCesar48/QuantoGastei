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
    
    # Páginas HTML
    path('', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('home/', home_view, name='home'),
    path('contas/', contas_view, name='contas'),
    path('transacoes/', transacoes_view, name='transacoes'),
    path('configuracoes/', configuracoes_view, name='configuracoes'),
    
    # API
    path('api/', include(router.urls)),
    
    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)