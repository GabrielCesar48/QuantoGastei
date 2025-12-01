from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para listagem e atualização de usuário."""
    
    is_pro = serializers.ReadOnlyField()
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'telefone',
            'foto_perfil',
            'plano',
            'is_pro',
            'data_expiracao_pro',
            'dark_mode',
            'notificacoes_ativas',
            'date_joined',
        ]
        read_only_fields = ['id', 'plano', 'data_expiracao_pro', 'date_joined']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuário (registro)."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
        ]
    
    def validate(self, data):
        """Valida se as senhas conferem."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não conferem.")
        return data
    
    def create(self, validated_data):
        """Cria usuário com senha criptografada."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        
        return usuario