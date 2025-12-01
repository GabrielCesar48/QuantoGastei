from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'plano', 'is_pro', 'date_joined']
    list_filter = ['plano', 'is_staff', 'date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Extras', {
            'fields': ('telefone', 'foto_perfil', 'plano', 'data_expiracao_pro')
        }),
        ('Preferências', {
            'fields': ('dark_mode', 'notificacoes_ativas')
        }),
    )