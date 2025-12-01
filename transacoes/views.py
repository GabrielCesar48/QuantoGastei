from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime
from .models import Categoria, Transacao
from .serializers import (
    CategoriaSerializer,
    TransacaoSerializer,
    TransacaoListSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriaSerializer
    
    def get_queryset(self):
        """Retorna categorias do usuário + categorias padrão do sistema."""
        return Categoria.objects.filter(
            Q(usuario=self.request.user) | Q(padrao=True)
        ).distinct()


class TransacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar transações.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['data', 'valor', 'created_at']
    search_fields = ['descricao', 'observacoes']
    
    def get_queryset(self):
        """Retorna apenas transações do usuário logado."""
        queryset = Transacao.objects.filter(usuario=self.request.user)
        
        # Filtros opcionais
        tipo = self.request.query_params.get('tipo')
        conta = self.request.query_params.get('conta')
        categoria = self.request.query_params.get('categoria')
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if conta:
            queryset = queryset.filter(
                Q(conta_origem_id=conta) | Q(conta_destino_id=conta)
            )
        
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        
        return queryset
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listagem."""
        if self.action == 'list':
            return TransacaoListSerializer
        return TransacaoSerializer
    
    @action(detail=False, methods=['get'])
    def resumo_mensal(self, request):
        """
        Retorna resumo financeiro do mês.
        Query params: mes (1-12), ano (ex: 2024)
        """
        mes = int(request.query_params.get('mes', timezone.now().month))
        ano = int(request.query_params.get('ano', timezone.now().year))
        
        transacoes = self.get_queryset().filter(
            data__year=ano,
            data__month=mes
        )
        
        receitas = transacoes.filter(tipo='receita').aggregate(
            total=Sum('valor')
        )['total'] or 0
        
        despesas = transacoes.filter(tipo='despesa').aggregate(
            total=Sum('valor')
        )['total'] or 0
        
        saldo = receitas - despesas
        
        # Gastos por categoria
        gastos_por_categoria = transacoes.filter(
            tipo='despesa',
            categoria__isnull=False
        ).values(
            'categoria__nome',
            'categoria__icone',
            'categoria__cor'
        ).annotate(
            total=Sum('valor')
        ).order_by('-total')
        
        return Response({
            'mes': mes,
            'ano': ano,
            'receitas': float(receitas),
            'despesas': float(despesas),
            'saldo': float(saldo),
            'gastos_por_categoria': list(gastos_por_categoria)
        })