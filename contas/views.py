from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conta
from .serializers import ContaSerializer, ContaListSerializer

class ContaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar contas financeiras.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas contas do usuário logado."""
        return Conta.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listagem."""
        if self.action == 'list':
            return ContaListSerializer
        return ContaSerializer