from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        """Apenas 'create' é público, resto precisa autenticação."""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Usa serializer específico para criação."""
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário logado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_preferences(self, request):
        """Atualiza preferências do usuário."""
        usuario = request.user
        
        # Atualiza apenas campos permitidos
        campos_permitidos = ['dark_mode', 'notificacoes_ativas', 'telefone']
        for campo in campos_permitidos:
            if campo in request.data:
                setattr(usuario, campo, request.data[campo])
        
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)
    
# Views para servir templates
def login_view(request):
    """Página de login."""
    return render(request, 'auth/login.html')

def registro_view(request):
    """Página de registro."""
    return render(request, 'auth/registro.html')


def home_view(request):
    """Dashboard principal."""
    return render(request, 'dashboard/home.html')


def contas_view(request):
    """Gerenciar contas."""
    return render(request, 'dashboard/contas.html')


def transacoes_view(request):
    """Gerenciar transações."""
    return render(request, 'dashboard/transacoes.html')


def configuracoes_view(request):
    """Página de configurações."""
    return render(request, 'dashboard/configuracoes.html')