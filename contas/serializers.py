from rest_framework import serializers
from .models import Conta

class ContaSerializer(serializers.ModelSerializer):
    """Serializer completo de Conta."""
    
    saldo_atual = serializers.ReadOnlyField()
    
    class Meta:
        model = Conta
        fields = [
            'id',
            'nome',
            'tipo',
            'saldo_inicial',
            'saldo_atual',
            'icone',
            'cor',
            'ativa',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        """Adiciona o usuário logado automaticamente."""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class ContaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem rápida."""
    
    saldo_atual = serializers.ReadOnlyField()
    
    class Meta:
        model = Conta
        fields = ['id', 'nome', 'tipo', 'saldo_atual', 'icone', 'cor', 'ativa']