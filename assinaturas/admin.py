from django.contrib import admin
from .models import Assinatura, LogPagamento

@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'plano', 'status', 'data_inicio', 'data_expiracao']
    list_filter = ['plano', 'status', 'renovacao_automatica']
    search_fields = ['usuario__username', 'order_id']

@admin.register(LogPagamento)
class LogPagamentoAdmin(admin.ModelAdmin):
    list_display = ['evento', 'assinatura', 'created_at']
    list_filter = ['evento', 'created_at']
    readonly_fields = ['payload']