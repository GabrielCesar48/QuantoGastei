from rest_framework import serializers
from .models import Categoria, Transacao
from contas.serializers import ContaListSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de Categoria."""
    
    class Meta:
        model = Categoria
        fields = [
            'id',
            'nome',
            'tipo',
            'icone',
            'cor',
            'padrao',
            'created_at',
        ]
        read_only_fields = ['id', 'padrao', 'created_at']
    
    def create(self, validated_data):
        """Adiciona o usuário logado automaticamente."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        return super().create(validated_data)


class TransacaoSerializer(serializers.ModelSerializer):
    """Serializer completo de Transação."""
    
    # Para exibição (nested)
    conta_origem_detalhes = ContaListSerializer(source='conta_origem', read_only=True)
    conta_destino_detalhes = ContaListSerializer(source='conta_destino', read_only=True)
    categoria_detalhes = CategoriaSerializer(source='categoria', read_only=True)
    
    # Para envio (IDs)
    conta_origem = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Será definido no __init__
    )
    conta_destino = serializers.PrimaryKeyRelatedField(
        queryset=None,
        required=False,
        allow_null=True
    )
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=None,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Transacao
        fields = [
            'id',
            'tipo',
            'conta_origem',
            'conta_origem_detalhes',
            'conta_destino',
            'conta_destino_detalhes',
            'categoria',
            'categoria_detalhes',
            'descricao',
            'valor',
            'data',
            'observacoes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def __init__(self, *args, **kwargs):
        """Define querysets baseado no usuário logado."""
        super().__init__(*args, **kwargs)
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            
            # Filtrar contas e categorias do usuário
            from contas.models import Conta
            
            self.fields['conta_origem'].queryset = Conta.objects.filter(usuario=user)
            self.fields['conta_destino'].queryset = Conta.objects.filter(usuario=user)
            self.fields['categoria'].queryset = Categoria.objects.filter(
                usuario=user
            ) | Categoria.objects.filter(padrao=True)
    
    def validate(self, data):
        """Validações de negócio."""
        tipo = data.get('tipo')
        conta_destino = data.get('conta_destino')
        conta_origem = data.get('conta_origem')
        
        # Transferência precisa de conta destino
        if tipo == 'transferencia':
            if not conta_destino:
                raise serializers.ValidationError(
                    "Transferência precisa de conta de destino."
                )
            if conta_origem == conta_destino:
                raise serializers.ValidationError(
                    "Não pode transferir para a mesma conta."
                )
        
        # Receita e Despesa não devem ter conta destino
        if tipo in ['receita', 'despesa'] and conta_destino:
            raise serializers.ValidationError(
                f"{tipo.capitalize()} não deve ter conta de destino."
            )
        
        return data
    
    def create(self, validated_data):
        """Adiciona o usuário logado automaticamente."""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class TransacaoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem."""
    
    conta_origem_nome = serializers.CharField(source='conta_origem.nome', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_icone = serializers.CharField(source='categoria.icone', read_only=True)
    
    class Meta:
        model = Transacao
        fields = [
            'id',
            'tipo',
            'descricao',
            'valor',
            'data',
            'conta_origem_nome',
            'categoria_nome',
            'categoria_icone',
        ]